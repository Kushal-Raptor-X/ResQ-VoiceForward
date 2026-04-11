"""
test_mongodb_integration.py — Test MongoDB integration and call logging.
"""
import asyncio
import sys

from config.db import close_db, connect_db, get_db, is_connected
from logCall import log_call


async def test_mongodb_connection():
    """Test MongoDB connection and call logging."""
    print("\n=== Testing MongoDB Integration ===\n")
    
    # Test connection
    print("1. Testing MongoDB connection...")
    success = await connect_db()
    
    if success:
        print("   ✓ Connected to MongoDB Atlas")
    else:
        print("   ✗ MongoDB connection failed (using in-memory fallback)")
    
    print(f"   Connection status: {is_connected()}")
    
    # Test call logging
    print("\n2. Testing call logging...")
    db = get_db()
    
    test_call_data = {
        "session_id": "test_session_123",
        "transcript": "Caller: I've been feeling really low lately.\nOperator: Can you tell me more?",
        "phrases": ["feeling low", "lately"],
        "risk_level": "MEDIUM",
        "risk_score": 45,
        "confidence": "HIGH",
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
    
    try:
        record_id = await log_call(db=db, **test_call_data)
        print(f"   ✓ Call logged successfully (ID: {record_id})")
    except Exception as e:
        print(f"   ✗ Call logging failed: {e}")
        await close_db()
        return False
    
    # Test fetching calls
    print("\n3. Testing call retrieval...")
    if db is not None:
        try:
            count = await db.calls.count_documents({})
            print(f"   ✓ Total calls in database: {count}")
            
            # Fetch the test call
            cursor = db.calls.find({"session_id": "test_session_123"}).limit(1)
            calls = await cursor.to_list(length=1)
            
            if calls:
                call = calls[0]
                print(f"   ✓ Retrieved test call:")
                print(f"     - Session ID: {call['session_id']}")
                print(f"     - Risk Level: {call['risk_level']}")
                print(f"     - Risk Score: {call['risk_score']}")
                print(f"     - Confidence: {call['confidence']}")
            else:
                print("   ✗ Could not retrieve test call")
        except Exception as e:
            print(f"   ✗ Call retrieval failed: {e}")
    else:
        print("   ⚠ Using in-memory storage (MongoDB offline)")
    
    # Test cleanup
    print("\n4. Cleaning up test data...")
    if db is not None:
        try:
            result = await db.calls.delete_many({"session_id": "test_session_123"})
            print(f"   ✓ Deleted {result.deleted_count} test records")
        except Exception as e:
            print(f"   ✗ Cleanup failed: {e}")
    
    # Close connection
    await close_db()
    print("\n=== Test Complete ===\n")
    return True


if __name__ == "__main__":
    try:
        asyncio.run(test_mongodb_connection())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
