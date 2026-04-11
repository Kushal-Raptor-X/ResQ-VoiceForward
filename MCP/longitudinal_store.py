"""
Layer 4 structured storage: JSON MVP (default) or PostgreSQL when configured.
Never persists raw transcripts — only timelines, anonymized IDs, aggregates.
"""

from __future__ import annotations

import json
import threading
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from kiro_config import load_ethical_config


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _default_data_dir() -> Path:
    cfg = load_ethical_config()
    override = (cfg.get("longitudinal_data_dir") or "").strip()
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "var" / "longitudinal"


class LongitudinalStoreBackend(ABC):
    @abstractmethod
    def save_call(self, record: dict) -> str:
        pass

    @abstractmethod
    def append_operator_action(
        self,
        call_id: str,
        action: str,
        phrase_fingerprint: Optional[str],
        phrase_redacted: Optional[str] = None,
    ) -> None:
        pass

    @abstractmethod
    def append_resource_usage(
        self, call_id: str, resource_label: str, followed: Optional[bool]
    ) -> None:
        pass

    @abstractmethod
    def update_call_outcome(self, call_id: str, outcome: str) -> None:
        pass

    @abstractmethod
    def merge_aggregated_patterns(self, key: str, value: dict) -> None:
        pass

    @abstractmethod
    def get_aggregated_patterns(self) -> dict[str, dict]:
        pass

    @abstractmethod
    def list_calls(self) -> list[dict]:
        pass

    @abstractmethod
    def purge_expired(self, retention_hours: float) -> int:
        pass


class JsonLongitudinalStore(LongitudinalStoreBackend):
    """File-backed store: JSONL for events, JSON blob for aggregates."""

    def __init__(self, base: Optional[Path] = None) -> None:
        self.base = base or _default_data_dir()
        self.base.mkdir(parents=True, exist_ok=True)
        self._calls_path = self.base / "calls.jsonl"
        self._op_path = self.base / "operator_actions.jsonl"
        self._res_path = self.base / "resource_usage.jsonl"
        self._agg_path = self.base / "aggregated_patterns.json"
        self._lock = threading.RLock()

    def _read_jsonl(self, path: Path) -> list[dict]:
        if not path.is_file():
            return []
        rows: list[dict] = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
        return rows

    def _append_jsonl(self, path: Path, obj: dict) -> None:
        with self._lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    def _read_agg(self) -> dict[str, dict]:
        if not self._agg_path.is_file():
            return {}
        with open(self._agg_path, encoding="utf-8") as f:
            return json.load(f)

    def _write_agg(self, data: dict[str, dict]) -> None:
        tmp = self._agg_path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(self._agg_path)

    def save_call(self, record: dict) -> str:
        call_id = record.get("call_id") or str(uuid.uuid4())
        record = {
            **record,
            "call_id": call_id,
            "created_at": record.get("created_at") or _utcnow().isoformat(),
        }
        self._append_jsonl(self._calls_path, record)
        return call_id

    def append_operator_action(
        self,
        call_id: str,
        action: str,
        phrase_fingerprint: Optional[str],
        phrase_redacted: Optional[str] = None,
    ) -> None:
        self._append_jsonl(
            self._op_path,
            {
                "call_id": call_id,
                "action": action,
                "phrase_fingerprint": phrase_fingerprint,
                "phrase_redacted": phrase_redacted,
                "created_at": _utcnow().isoformat(),
            },
        )

    def append_resource_usage(
        self, call_id: str, resource_label: str, followed: Optional[bool]
    ) -> None:
        self._append_jsonl(
            self._res_path,
            {
                "call_id": call_id,
                "resource_label": resource_label,
                "followed": followed,
                "suggested_at": _utcnow().isoformat(),
            },
        )

    def update_call_outcome(self, call_id: str, outcome: str) -> None:
        with self._lock:
            rows = self._read_jsonl(self._calls_path)
            changed = False
            for r in rows:
                if r.get("call_id") == call_id:
                    r["final_outcome"] = outcome
                    changed = True
            if not changed:
                return
            tmp = self._calls_path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            tmp.replace(self._calls_path)

    def merge_aggregated_patterns(self, key: str, value: dict) -> None:
        with self._lock:
            agg = self._read_agg()
            cur = agg.get(key, {})
            if isinstance(cur, dict) and isinstance(value, dict):
                cur.update(value)
                agg[key] = cur
            else:
                agg[key] = value
            self._write_agg(agg)

    def get_aggregated_patterns(self) -> dict[str, dict]:
        with self._lock:
            return dict(self._read_agg())

    def list_calls(self) -> list[dict]:
        with self._lock:
            return self._read_jsonl(self._calls_path)

    def list_operator_actions(self) -> list[dict]:
        with self._lock:
            return self._read_jsonl(self._op_path)

    def list_resource_usage(self) -> list[dict]:
        with self._lock:
            return self._read_jsonl(self._res_path)

    def purge_expired(self, retention_hours: float) -> int:
        if retention_hours <= 0:
            return 0
        cutoff = _utcnow() - timedelta(hours=retention_hours)
        with self._lock:
            rows = self._read_jsonl(self._calls_path)
            kept = []
            removed = 0
            for r in rows:
                created = r.get("created_at")
                if not created:
                    kept.append(r)
                    continue
                try:
                    ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
                except ValueError:
                    kept.append(r)
                    continue
                if ts < cutoff:
                    removed += 1
                else:
                    kept.append(r)
            tmp = self._calls_path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                for r in kept:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            tmp.replace(self._calls_path)
            return removed


class PostgresLongitudinalStore(LongitudinalStoreBackend):
    """Optional PostgreSQL backend (sync psycopg2)."""

    def __init__(self, dsn: str) -> None:
        import psycopg2
        from psycopg2.extras import Json

        self._psycopg2 = psycopg2
        self._Json = Json
        self._dsn = dsn
        self._lock = threading.Lock()

    def _conn(self):
        return self._psycopg2.connect(self._dsn)

    def save_call(self, record: dict) -> str:
        call_id = record.get("call_id") or str(uuid.uuid4())
        record = {**record, "call_id": call_id}
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO calls (
                        call_id, anonymized_session_id, risk_timeline, final_outcome,
                        stt_reliable, created_at, expires_at, transcript_embedding, metadata
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (call_id) DO UPDATE SET
                        risk_timeline = EXCLUDED.risk_timeline,
                        final_outcome = EXCLUDED.final_outcome,
                        stt_reliable = EXCLUDED.stt_reliable,
                        metadata = EXCLUDED.metadata
                    """,
                    (
                        call_id,
                        record["anonymized_session_id"],
                        self._Json(record.get("risk_timeline", [])),
                        record.get("final_outcome", "unknown"),
                        record.get("stt_reliable", True),
                        record.get("created_at") or _utcnow(),
                        record.get("expires_at"),
                        record.get("transcript_embedding"),
                        self._Json(record.get("metadata", {})),
                    ),
                )
            c.commit()
        return call_id

    def append_operator_action(
        self,
        call_id: str,
        action: str,
        phrase_fingerprint: Optional[str],
        phrase_redacted: Optional[str] = None,
    ) -> None:
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO operator_actions (call_id, action, phrase_fingerprint, phrase_redacted)
                    VALUES (%s,%s,%s,%s)
                    """,
                    (call_id, action, phrase_fingerprint, phrase_redacted),
                )
            c.commit()

    def append_resource_usage(
        self, call_id: str, resource_label: str, followed: Optional[bool]
    ) -> None:
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO resource_usage (call_id, resource_label, followed)
                    VALUES (%s,%s,%s)
                    """,
                    (call_id, resource_label, followed),
                )
            c.commit()

    def update_call_outcome(self, call_id: str, outcome: str) -> None:
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    "UPDATE calls SET final_outcome = %s WHERE call_id::text = %s",
                    (outcome, call_id),
                )
            c.commit()

    def merge_aggregated_patterns(self, key: str, value: dict) -> None:
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    "SELECT pattern_value FROM aggregated_patterns WHERE pattern_key = %s",
                    (key,),
                )
                row = cur.fetchone()
                existing: dict = {}
                if row and row[0]:
                    existing = dict(row[0]) if isinstance(row[0], dict) else {}
                merged = {**existing, **value}
                cur.execute(
                    """
                    INSERT INTO aggregated_patterns (pattern_key, pattern_value, updated_at)
                    VALUES (%s, %s, NOW())
                    ON CONFLICT (pattern_key) DO UPDATE SET
                        pattern_value = EXCLUDED.pattern_value,
                        updated_at = NOW()
                    """,
                    (key, self._Json(merged)),
                )
            c.commit()

    def get_aggregated_patterns(self) -> dict[str, dict]:
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT pattern_key, pattern_value FROM aggregated_patterns")
                rows = cur.fetchall()
        return {k: dict(v) if v else {} for k, v in rows}

    def list_calls(self) -> list[dict]:
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    """
                    SELECT call_id::text, anonymized_session_id, risk_timeline, final_outcome,
                           stt_reliable, created_at, metadata
                    FROM calls ORDER BY created_at
                    """
                )
                cols = [d[0] for d in cur.description]
                raw = cur.fetchall()
        out: list[dict] = []
        for row in raw:
            out.append(dict(zip(cols, row)))
        return out

    def purge_expired(self, retention_hours: float) -> int:
        if retention_hours <= 0:
            return 0
        cutoff = _utcnow() - timedelta(hours=retention_hours)
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute("DELETE FROM calls WHERE created_at < %s RETURNING call_id", (cutoff,))
                n = len(cur.fetchall())
            c.commit()
        return n

    def list_operator_actions(self) -> list[dict]:
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    """
                    SELECT call_id::text, action, phrase_fingerprint, phrase_redacted, created_at
                    FROM operator_actions
                    """
                )
                cols = [d[0] for d in cur.description]
                raw = cur.fetchall()
        return [dict(zip(cols, row)) for row in raw]

    def list_resource_usage(self) -> list[dict]:
        with self._lock, self._conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    """
                    SELECT call_id::text, resource_label, followed, suggested_at
                    FROM resource_usage
                    """
                )
                cols = [d[0] for d in cur.description]
                raw = cur.fetchall()
        return [dict(zip(cols, row)) for row in raw]


def get_longitudinal_store() -> LongitudinalStoreBackend:
    cfg = load_ethical_config()
    use_pg = bool(cfg.get("use_postgresql"))
    dsn = (cfg.get("postgresql_dsn") or "").strip()
    if use_pg and dsn:
        try:
            return PostgresLongitudinalStore(dsn)
        except Exception:
            pass
    return JsonLongitudinalStore()
