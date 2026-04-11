"""
Layer 4 — Longitudinal pattern intelligence (offline learning + aggregates).
No raw transcript retention; uses privacy_filter + fingerprints where needed.
"""

from __future__ import annotations

import hashlib
import math
import threading
import uuid
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar, Optional

from kiro_config import load_ethical_config
from longitudinal_store import get_longitudinal_store
from privacy_filter import privacy_filter


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


RISK_NUM = {
    "LOW": 0.2,
    "MEDIUM": 0.5,
    "MED": 0.5,
    "HIGH": 0.8,
    "CRITICAL": 1.0,
    "unknown": 0.35,
}


def _risk_to_num(level: str) -> float:
    if not level:
        return 0.35
    return RISK_NUM.get(str(level).upper(), RISK_NUM.get(str(level), 0.45))


class PatternEngine:
    """
    In-memory active call buffers + longitudinal store persistence.
    Learning job updates aggregated_patterns for supervisor insights.
    """

    _open: ClassVar[dict[str, dict]] = {}
    _lock = threading.RLock()
    _lr_weights: ClassVar[Optional[list[float]]] = None
    _lr_bias: ClassVar[float] = 0.0
    _model_trained: ClassVar[bool] = False

    def __init__(self) -> None:
        self.store = get_longitudinal_store()

    # ------------------------------------------------------------------
    # Session lifecycle (real-time path — memory only until close)
    # ------------------------------------------------------------------

    def open_call_session(self, anonymized_session_id: str) -> str:
        call_id = str(uuid.uuid4())
        cfg = load_ethical_config()
        retention_h = float(cfg.get("data_retention_hours", 72))
        with self._lock:
            self._open[call_id] = {
                "anonymized_session_id": anonymized_session_id,
                "risk_timeline": [],
                "stt_reliable": True,
                "metadata": {},
                "expires_at": (_utcnow() + timedelta(hours=retention_h)).isoformat(),
            }
        return call_id

    def set_stt_unreliable(self, call_id: str) -> None:
        with self._lock:
            if call_id in self._open:
                self._open[call_id]["stt_reliable"] = False

    def record_risk_tick(
        self,
        call_id: str,
        elapsed_minutes: float,
        risk_level: str,
        *,
        stt_confidence: Optional[float] = None,
    ) -> None:
        point = {
            "t_minutes": round(float(elapsed_minutes), 2),
            "risk": str(risk_level).upper(),
            "risk_numeric": _risk_to_num(risk_level),
            "stt_confidence": stt_confidence,
        }
        with self._lock:
            buf = self._open.get(call_id)
            if buf:
                buf["risk_timeline"].append(point)

    def close_call_session(self, call_id: str, final_outcome: str) -> None:
        with self._lock:
            buf = self._open.pop(call_id, None)
        if not buf:
            return
        allowed = {"resolved", "escalated", "dropped", "unknown"}
        outcome = final_outcome if final_outcome in allowed else "unknown"
        self.store.save_call(
            {
                "call_id": call_id,
                "anonymized_session_id": buf["anonymized_session_id"],
                "risk_timeline": buf["risk_timeline"],
                "final_outcome": outcome,
                "stt_reliable": buf.get("stt_reliable", True),
                "metadata": buf.get("metadata", {}),
                "expires_at": buf.get("expires_at"),
            }
        )

    def record_operator_action(
        self, call_id: str, action: str, phrase: Optional[str] = None
    ) -> None:
        action_l = action.lower()
        if action_l not in {"accepted", "modified", "rejected"}:
            action_l = "modified"
        fp: Optional[str] = None
        snippet: Optional[str] = None
        if phrase:
            clean, _ = privacy_filter(phrase)
            snippet = clean.strip()[:120] or None
            if snippet:
                fp = hashlib.sha256(snippet.lower().encode()).hexdigest()[:24]
        self.store.append_operator_action(call_id, action_l, fp, snippet)

    def record_resource_suggestion(
        self, call_id: str, resource_label: str, followed: Optional[bool] = None
    ) -> None:
        clean, _ = privacy_filter(resource_label)
        self.store.append_resource_usage(call_id, clean[:200], followed)

    # ------------------------------------------------------------------
    # Early risk (minute 1–5 → escalation proxy)
    # ------------------------------------------------------------------

    @classmethod
    def early_feature_vector(cls, timeline: list[dict]) -> dict[str, float]:
        window = [p for p in timeline if float(p.get("t_minutes", 999)) <= 5.0]
        if not window:
            return {
                "mean_risk_1_5": 0.35,
                "max_risk_1_5": 0.35,
                "min_risk_1_5": 0.35,
                "high_frac": 0.0,
                "stt_mean": 1.0,
                "n_points": 0.0,
            }
        nums = [float(p.get("risk_numeric", 0.35)) for p in window]
        highs = sum(1 for p in window if str(p.get("risk")).upper() in {"HIGH", "CRITICAL"})
        stts = [float(p["stt_confidence"]) for p in window if p.get("stt_confidence") is not None]
        stt_mean = sum(stts) / len(stts) if stts else 1.0
        return {
            "mean_risk_1_5": sum(nums) / len(nums),
            "max_risk_1_5": max(nums),
            "min_risk_1_5": min(nums),
            "high_frac": highs / max(len(window), 1),
            "stt_mean": stt_mean,
            "n_points": float(len(window)),
        }

    def predict_early_risk_score(self, call_id: str) -> dict[str, Any]:
        with self._lock:
            buf = self._open.get(call_id)
            timeline = list(buf["risk_timeline"]) if buf else []
        feats = self.early_feature_vector(timeline)
        ordered = [
            feats["mean_risk_1_5"],
            feats["max_risk_1_5"],
            feats["min_risk_1_5"],
            feats["high_frac"],
            feats["stt_mean"],
            feats["n_points"] / 10.0,
        ]
        score = self._score_with_model(ordered, feats)
        return {"early_risk_score": round(score, 4), "features": feats}

    def _score_with_model(self, ordered: list[float], feats: dict[str, float]) -> float:
        if self._model_trained and self._lr_weights and len(self._lr_weights) == len(ordered):
            z = sum(w * x for w, x in zip(self._lr_weights, ordered)) + self._lr_bias
            return float(1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, z)))))
        base = 0.2 + 0.55 * feats["max_risk_1_5"] + 0.2 * feats["high_frac"]
        if feats["stt_mean"] < 0.65:
            base += 0.1
        return min(0.97, max(0.03, base))

    # ------------------------------------------------------------------
    # Offline batch learning
    # ------------------------------------------------------------------

    def run_offline_batch_learning(self) -> dict[str, Any]:
        cfg = load_ethical_config()
        min_samples = int(cfg.get("batch_learning_min_samples", 20))
        calls = self.store.list_calls()
        X: list[list[float]] = []
        y: list[int] = []

        for c in calls:
            tl = c.get("risk_timeline") or []
            if not tl:
                continue
            fv = self.early_feature_vector(tl)
            vec = [
                fv["mean_risk_1_5"],
                fv["max_risk_1_5"],
                fv["min_risk_1_5"],
                fv["high_frac"],
                fv["stt_mean"],
                fv["n_points"] / 10.0,
            ]
            outcome = (c.get("final_outcome") or "unknown").lower()
            late_high = any(
                float(p.get("t_minutes", 0)) >= 18.0
                and str(p.get("risk")).upper() in {"HIGH", "CRITICAL"}
                for p in tl
            )
            label = 1 if outcome == "escalated" or late_high else 0
            X.append(vec)
            y.append(label)

        report: dict[str, Any] = {"samples_used": len(X), "model": "heuristic"}
        if len(X) >= min_samples:
            try:
                from sklearn.linear_model import LogisticRegression

                clf = LogisticRegression(max_iter=300, class_weight="balanced")
                clf.fit(X, y)
                PatternEngine._lr_weights = clf.coef_[0].tolist()
                PatternEngine._lr_bias = float(clf.intercept_[0])
                PatternEngine._model_trained = True
                report["model"] = "logistic_regression"
                report["weights"] = PatternEngine._lr_weights
            except Exception as e:
                report["model_error"] = str(e)

        phrase_stats = self._compute_phrase_effectiveness()
        resource_stats = self._compute_resource_effectiveness()
        self.store.merge_aggregated_patterns(
            "last_batch",
            {
                "computed_at": _utcnow().isoformat(),
                "phrase_top": phrase_stats[:15],
                "resource_top": resource_stats[:15],
            },
        )
        return report

    def phrase_effectiveness(self, limit: int = 20) -> list[dict[str, Any]]:
        try:
            return self._compute_phrase_effectiveness()[:limit]
        except Exception:
            agg = self.store.get_aggregated_patterns()
            return list(agg.get("last_batch", {}).get("phrase_top", []))[:limit]

    def resource_effectiveness(self, limit: int = 20) -> list[dict[str, Any]]:
        try:
            return self._compute_resource_effectiveness()[:limit]
        except Exception:
            agg = self.store.get_aggregated_patterns()
            return list(agg.get("last_batch", {}).get("resource_top", []))[:limit]

    def _compute_phrase_effectiveness(self) -> list[dict[str, Any]]:
        calls = {c["call_id"]: c for c in self.store.list_calls()}
        op_fn = getattr(self.store, "list_operator_actions", None)
        if not callable(op_fn):
            return []
        actions = op_fn()
        by_phrase: dict[str, dict[str, Any]] = {}
        for a in actions:
            cid = a.get("call_id")
            fp = a.get("phrase_fingerprint")
            phrase_label = a.get("phrase_redacted") or (f"hash:{fp[:10]}…" if fp else None)
            if not fp and not phrase_label:
                continue
            key = fp or phrase_label
            call = calls.get(cid, {})
            outcome = (call.get("final_outcome") or "unknown").lower()
            action = (a.get("action") or "").lower()
            success = outcome == "resolved" and action == "accepted"
            bucket = by_phrase.setdefault(
                key,
                {"phrase": phrase_label or key, "wins": 0, "total": 0},
            )
            if phrase_label and not phrase_label.startswith("hash:"):
                bucket["phrase"] = phrase_label
            bucket["total"] += 1
            if success:
                bucket["wins"] += 1
        out = []
        for _fp, b in by_phrase.items():
            t = max(b["total"], 1)
            out.append(
                {
                    "phrase": b["phrase"],
                    "success_rate": round(b.get("wins", 0) / t, 4),
                    "samples": t,
                }
            )
        out.sort(key=lambda x: -x["success_rate"])
        return out

    def _compute_resource_effectiveness(self) -> list[dict[str, Any]]:
        fn = getattr(self.store, "list_resource_usage", None)
        if not callable(fn):
            return []
        usage = fn()
        by_res: dict[str, dict[str, int]] = defaultdict(lambda: {"suggested": 0, "followed": 0})
        for u in usage:
            label = u.get("resource_label") or "unknown"
            by_res[label]["suggested"] += 1
            if u.get("followed") is True:
                by_res[label]["followed"] += 1
        out = []
        for res, ctr in by_res.items():
            s = max(ctr["suggested"], 1)
            out.append(
                {
                    "resource": res,
                    "follow_through_rate": round(ctr["followed"] / s, 4),
                    "suggested_count": ctr["suggested"],
                }
            )
        out.sort(key=lambda x: -x["follow_through_rate"])
        return out

    def build_supervisor_insights(self) -> dict[str, Any]:
        cfg = load_ethical_config()
        retention = float(cfg.get("data_retention_hours", 72))
        removed = self.store.purge_expired(retention)

        phrases = self.phrase_effectiveness(10)
        top_effective = [
            {"phrase": p["phrase"], "success_rate": p["success_rate"]}
            for p in phrases
            if p.get("samples", 0) >= 2
        ]

        calls = self.store.list_calls()
        high_risk_patterns: list[dict[str, Any]] = []
        for c in calls:
            tl = c.get("risk_timeline") or []
            if not tl:
                continue
            fv = self.early_feature_vector(tl)
            vec = [
                fv["mean_risk_1_5"],
                fv["max_risk_1_5"],
                fv["min_risk_1_5"],
                fv["high_frac"],
                fv["stt_mean"],
                fv["n_points"] / 10.0,
            ]
            score = self._score_with_model(vec, fv)
            outcome = (c.get("final_outcome") or "").lower()
            if score >= 0.65 and outcome in {"escalated", "unknown"}:
                high_risk_patterns.append(
                    {
                        "call_id": c.get("call_id"),
                        "early_risk_score": round(score, 3),
                        "outcome": outcome or "unknown",
                        "signal": "strong early elevation with escalation or open outcome",
                    }
                )
        high_risk_patterns = sorted(
            high_risk_patterns, key=lambda x: -x["early_risk_score"]
        )[:10]

        resources = self.resource_effectiveness(30)
        resource_gaps = [
            {
                "resource": r["resource"],
                "follow_through_rate": r["follow_through_rate"],
                "suggested_count": r["suggested_count"],
            }
            for r in resources
            if r["suggested_count"] >= 2 and r["follow_through_rate"] < 0.45
        ][:10]

        return {
            "top_effective_phrases": top_effective[:8],
            "high_risk_patterns": high_risk_patterns,
            "resource_gaps": resource_gaps,
            "maintenance": {"purged_expired_records": removed},
        }


_engine_instance: Optional[PatternEngine] = None


def get_pattern_engine() -> PatternEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = PatternEngine()
    return _engine_instance


def reset_pattern_engine_singleton() -> None:
    global _engine_instance
    _engine_instance = None
