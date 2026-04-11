"""
config/db.py — MongoDB Atlas connection manager.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_ROOT / ".env")
load_dotenv()  # cwd fallback

MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/voiceforward")

# Parse DB name from URI path segment before any query string
_path = MONGO_URI.split("/")[-1].split("?")[0]
DB_NAME: str = _path if _path else "voiceforward"

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None
_connected: bool = False


async def connect_db() -> bool:
    global _client, _db, _connected

    if "<user>" in MONGO_URI or "<password>" in MONGO_URI or "USER:PASSWORD" in MONGO_URI:
        print("[db] ✗ MONGO_URI still has placeholder values — set MONGO_URI in backend/.env")
        return False

    print(f"[db] Connecting to MongoDB Atlas (db='{DB_NAME}')...")
    try:
        # For Atlas SRV URIs, TLS is handled automatically by the URI scheme
        _client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        await _client.admin.command("ping")
        _db = _client[DB_NAME]
        _connected = True

        # Create indexes for analytics performance
        await _db.calls.create_index("session_id")
        await _db.calls.create_index("risk_level")
        await _db.calls.create_index("operator_action")
        await _db.calls.create_index([("created_at", -1)])
        await _db.calls.create_index([("session_id", 1), ("created_at", -1)])

        await _db.audit_decisions.create_index("session_id")
        await _db.audit_decisions.create_index([("timestamp", -1)])
        await _db.audit_decisions.create_index("record_id")

        count = await _db.calls.count_documents({})
        print(f"[db] ✓ Connected to MongoDB Atlas — '{DB_NAME}' ({count} existing records)")
        return True
    except Exception as e:
        _connected = False
        _db = None
        print(f"[db] ✗ MongoDB connection failed: {type(e).__name__}: {str(e)[:150]}")
        print("[db]   Running with in-memory fallback.")
        return False


def get_db() -> Optional[AsyncIOMotorDatabase]:
    return _db if _connected else None


def is_connected() -> bool:
    return _connected


async def close_db() -> None:
    global _client, _connected
    if _client:
        _client.close()
        _connected = False
        print("[db] MongoDB connection closed.")
