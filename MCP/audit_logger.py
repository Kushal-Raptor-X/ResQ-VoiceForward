"""
Layer 5 — Append-only, hash-chained audit log for every AI decision.
Background writer thread keeps the hot path non-blocking.
"""

from __future__ import annotations

import hashlib
import json
import queue
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from kiro_config import load_ethical_config
from privacy_filter import privacy_filter

_GENESIS = "0" * 64
_SENTINEL = object()


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_dumps(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _audit_path() -> Path:
    cfg = load_ethical_config()
    override = (cfg.get("audit_log_path") or "").strip()
    if override:
        return Path(override)
    base = Path(__file__).resolve().parent / "var" / "audit"
    base.mkdir(parents=True, exist_ok=True)
    return base / "decisions.jsonl"


def _failure_path() -> Path:
    base = Path(__file__).resolve().parent / "var" / "audit"
    base.mkdir(parents=True, exist_ok=True)
    return base / "failures.jsonl"


class AuditLogger:
    _instance: Optional["AuditLogger"] = None
    _instance_lock = threading.Lock()

    def __init__(self) -> None:
        self._path = _audit_path()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._queue: queue.Queue[Any] = queue.Queue(maxsize=50_000)
        self._thread: Optional[threading.Thread] = None
        self._last_hash = _GENESIS
        self._hash_lock = threading.Lock()
        self._load_tail_hash()

    def _load_tail_hash(self) -> None:
        if not self._path.is_file():
            self._last_hash = _GENESIS
            return
        last = _GENESIS
        try:
            with open(self._path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    row = json.loads(line)
                    last = row.get("chain_hash", last)
        except Exception:
            last = _GENESIS
        self._last_hash = last

    @classmethod
    def instance(cls) -> "AuditLogger":
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = AuditLogger()
                cls._instance._ensure_worker()
            return cls._instance

    @classmethod
    def reset_for_tests(cls) -> None:
        with cls._instance_lock:
            if cls._instance and cls._instance._thread and cls._instance._thread.is_alive():
                cls._instance._queue.put(_SENTINEL)
                cls._instance._thread.join(timeout=2.0)
            cls._instance = None

    def _ensure_worker(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        def _worker() -> None:
            while True:
                item = self._queue.get()
                if item is _SENTINEL:
                    break
                try:
                    self._write_one(item)
                except Exception as e:
                    print(f"[audit_logger] write error: {e}")

        self._thread = threading.Thread(target=_worker, name="audit-writer", daemon=True)
        self._thread.start()

    def _write_one(self, payload: dict) -> None:
        with self._hash_lock:
            prev = self._last_hash
            body = dict(payload)
            body["prev_chain_hash"] = prev
            chain_input = prev + _canonical_dumps(body)
            chain_hash = hashlib.sha256(chain_input.encode("utf-8")).hexdigest()
            body["chain_hash"] = chain_hash
            self._last_hash = chain_hash
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(_canonical_dumps(body) + "\n")

    def enqueue_decision(
        self,
        *,
        session_id: str,
        input_text: str,
        risk: str,
        confidence: float,
        reasoning: dict[str, Any],
        operator_action: str = "pending",
        extra: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        self._ensure_worker()
        redacted, redactions = privacy_filter(input_text)
        record: dict[str, Any] = {
            "timestamp": _utc_iso(),
            "session_id": session_id,
            "input_text": redacted,
            "privacy_redactions": redactions,
            "risk": risk,
            "confidence": float(confidence),
            "reasoning": reasoning,
            "operator_action": operator_action,
        }
        if extra:
            record["extra"] = extra
        try:
            self._queue.put_nowait(record)
        except queue.Full:
            return {"queued": False, "error": "audit queue full — decision not logged"}
        return {"queued": True, "redactions": redactions}

    def replay_call(self, session_id: str) -> dict[str, Any]:
        if not self._path.is_file():
            return {"session_id": session_id, "timeline": [], "count": 0}
        events: list[dict[str, Any]] = []
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("session_id") != session_id:
                    continue
                events.append(row)
        events.sort(key=lambda r: r.get("timestamp", ""))
        return {"session_id": session_id, "timeline": events, "count": len(events)}

    def verify_chain(self, max_lines: int = 100_000) -> dict[str, Any]:
        if not self._path.is_file():
            return {"ok": True, "verified_lines": 0}
        prev = _GENESIS
        count = 0
        with open(self._path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                ch = row.get("chain_hash")
                p = row.get("prev_chain_hash")
                if p != prev:
                    return {
                        "ok": False,
                        "broken_at_line": count,
                        "reason": "prev_hash_mismatch",
                    }
                body = {k: v for k, v in row.items() if k != "chain_hash"}
                expected = hashlib.sha256(
                    (p + _canonical_dumps(body)).encode("utf-8")
                ).hexdigest()
                if ch != expected:
                    return {
                        "ok": False,
                        "broken_at_line": count,
                        "reason": "chain_hash_mismatch",
                    }
                prev = ch
                count += 1
                if count >= max_lines:
                    break
        return {"ok": True, "verified_lines": count}


def append_failure_record(
    failure_type: str,
    detail: str,
    session_id: Optional[str] = None,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    rec = {
        "timestamp": _utc_iso(),
        "failure_type": failure_type,
        "detail": detail[:2000],
        "session_id": session_id,
    }
    if extra:
        rec["extra"] = extra
    path = _failure_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return {"logged": True, "path": str(path)}
