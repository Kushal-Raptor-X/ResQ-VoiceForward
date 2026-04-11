"""
fix_existing_records.py — Add missing fields to existing MongoDB records.
"""
import asyncio

from config.db import close_db, connect_db, get_db


async def fix_records():
    """Add missing fields to existing records."""
    print("\n=== Fixing Existing MongoDB Records ===\n")
    
    # Connect
    await connect_db()
    db = get_db()
    
    if db is None:
        print("MongoDB not connected")
        return
    
    # Find records missing risk_score
    print("1. Checking for records missing risk_score...")
    missing_score = await db.calls.count_documents({"risk_score": {"$exists": False}})
    print(f"   Found {missing_score} records missing risk_score")
    
    if missing_score > 0:
        print("   Adding risk_score=0 to these records...")
        result = await db.calls.update_many(
            {"risk_score": {"$exists": False}},
            {"$set": {"risk_score": 0}}
        )
        print(f"   ✓ Updated {result.modified_count} records")
    
    # Find records with float confidence (should be string)
    print("\n2. Checking for records with numeric confidence...")
    numeric_confidence = await db.calls.count_documents({"confidence": {"$type": "number"}})
    print(f"   Found {numeric_confidence} records with numeric confidence")
    
    if numeric_confidence > 0:
        print("   Converting to string 'MEDIUM'...")
        result = await db.calls.update_many(
            {"confidence": {"$type": "number"}},
            {"$set": {"confidence": "MEDIUM"}}
        )
        print(f"   ✓ Updated {result.modified_count} records")
    
    # Verify all records
    print("\n3. Verifying all records...")
    total = await db.calls.count_documents({})
    print(f"   Total records: {total}")
    
    cursor = db.calls.find().limit(5)
    calls = await cursor.to_list(length=5)
    
    print(f"\n   Sample records:")
    for call in calls:
        print(f"   - {call.get('session_id', 'N/A')}: risk_score={call.get('risk_score', 'MISSING')}, confidence={call.get('confidence', 'MISSING')}")
    
    await close_db()
    print("\n=== Fix Complete ===\n")


if __name__ == "__main__":
    asyncio.run(fix_records())
