"""
utils/cache.py — Thread-safe in-memory cache with TTL.
Used by resource_agent to avoid redundant API calls.
"""
import time
from typing import Any, Optional


class TTLCache:
    """Simple TTL cache. No external deps."""

    def __init__(self, ttl_seconds: int = 300):
        self._store: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (value, time.monotonic() + self._ttl)

    def clear(self) -> None:
        self._store.clear()


# Shared instances
resource_cache = TTLCache(ttl_seconds=300)   # 5 min for resource queries
stt_cache = TTLCache(ttl_seconds=60)         # 1 min for repeated audio
