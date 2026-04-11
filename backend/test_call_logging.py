"""
test_call_logging.py — Test that calls are being logged correctly during analysis.
"""
import asyncio
import sys

from config.db import close_db, connect_db, get_db
from logCall import log_call


async def test_call_logging():
    """Test the complete call logging flow."""
    print("\n=== Testing Call Logging Flow ===\n")
    
    # Connect to MongoDB
    print("1. Connecting to MongoDB...")
    success = await connect_db()
    if not success:
        print("   ✗ MongoDB connection failed")
        return False
    print("   ✓ Connected to MongoDB Atlas")
    
    db = get_db()
    
    # Simulate a real analysis result
    print("\n2. Simulating AI analysis result...")
    test_analysis = {
        "session_id": "test_live_call_456",
        "transcript": "[00:01:23] CALLER: I've been feeling really low lately.\n[00:01:45] OPERATOR: Can you tell me more about that?",
        "phrases": ["feeling low", "lately"],
        "risk_level": "MEDIUM",
        "risk_score": 55,
        "confidence": "HIGH",  # String, not float
        "reasoning": ["Caller expressed low mood but no immediate danger signals"],
        "agent_verdicts": {
            "language_agent": "MEDIUM - mood-related language detected",
            "emotion_agent": "MEDIUM - subdued tone",
            "narrative_agent": "LOW - no crisis narrative"
        },
        "triggered_signals": ["feeling low"],
        "suggested_response": "I hear that you're going through a difficult time. What's been happening?",
        "operator_action": "pending",
        "outcome": "unknown",
    }
    
    # Log the call
    print("\n3. Logging call to MongoDB...")
    try:
        record_id = await log_call(db=db, **test_analysis)
        print(f"   ✓ Call logged successfully")
        print(f"   Record ID: {record_id}")
    except Exception as e:
        print(f"   ✗ Failed to log call: {e}")
        import traceback
        traceback.print_exc()
        await close_db()
        return False
    
    # Verify the call was stored
    print("\n4. Verifying call was stored...")
    try:
        count = await db.calls.count_documents({"session_id": "test_live_call_456"})
        print(f"   ✓ Found {count} call(s) with session_id 'test_live_call_456'")
        
        # Fetch the call
        call = await db.calls.find_one({"session_id": "test_live_call_456"})
        if call:
            print(f"\n   Call Details:")
            print(f"   - Session ID: {call['session_id']}")
            print(f"   - Risk Level: {call['risk_level']}")
            print(f"   - Risk Score: {call['risk_score']}")
            print(f"   - Confidence: {call['confidence']}")
            print(f"   - Operator Action: {call['operator_action']}")
            print(f"   - Triggered Signals: {call['triggered_signals']}")
            print(f"   - Created At: {call['created_at']}")
    except Exception as e:
        print(f"   ✗ Failed to verify: {e}")
    
    # Test fetching via REST API format
    print("\n5. Testing REST API format (GET /calls)...")
    try:
        cursor = db.calls.find().sort("created_at", -1).limit(5)
        calls = await cursor.to_list(length=5)
        
        print(f"   ✓ Found {len(calls)} recent calls:")
        for i, call in enumerate(calls, 1):
            print(f"   {i}. {call['session_id']} - {call['risk_level']} ({call['risk_score']}/100) - {call['confidence']}")
    except Exception as e:
        print(f"   ✗ Failed to fetch calls: {e}")
    
    # Cleanup
    print("\n6. Cleaning up test data...")
    try:
        result = await db.calls.delete_many({"session_id": "test_live_call_456"})
        print(f"   ✓ Deleted {result.deleted_count} test records")
    except Exception as e:
        print(f"   ✗ Cleanup failed: {e}")
    
    await close_db()
    print("\n=== Test Complete ===\n")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_call_logging())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
