"""
debug_call_history.py — Debug why call history isn't showing up.
"""
import asyncio
import json

from config.db import close_db, connect_db, get_db


async def debug():
    """Debug call history issues."""
    print("\n" + "="*60)
    print("DEBUGGING CALL HISTORY")
    print("="*60 + "\n")
    
    # Step 1: Connect to MongoDB
    print("STEP 1: Connecting to MongoDB...")
    success = await connect_db()
    if not success:
        print("   ✗ FAILED: MongoDB connection failed")
        print("   → Check MONGO_URI in backend/.env")
        return
    print("   ✓ SUCCESS: Connected to MongoDB Atlas\n")
    
    db = get_db()
    
    # Step 2: Check if calls collection exists
    print("STEP 2: Checking calls collection...")
    collections = await db.list_collection_names()
    print(f"   Available collections: {collections}")
    
    if "calls" not in collections:
        print("   ✗ WARNING: 'calls' collection doesn't exist yet")
        print("   → This is normal if no calls have been logged")
        print("   → Start a call in the UI to create the collection\n")
    else:
        print("   ✓ SUCCESS: 'calls' collection exists\n")
    
    # Step 3: Count documents
    print("STEP 3: Counting documents in calls collection...")
    try:
        count = await db.calls.count_documents({})
        print(f"   Total documents: {count}")
        
        if count == 0:
            print("   ✗ WARNING: No calls in database")
            print("   → Start a call in the UI to log data")
            print("   → Make sure backend is running: python main.py")
            print("   → Make sure you click 'Start Call Transcript' button\n")
        else:
            print(f"   ✓ SUCCESS: Found {count} call(s)\n")
    except Exception as e:
        print(f"   ✗ ERROR: {e}\n")
        await close_db()
        return
    
    # Step 4: Fetch and display calls
    if count > 0:
        print("STEP 4: Fetching recent calls...")
        try:
            cursor = db.calls.find().sort("created_at", -1).limit(5)
            calls = await cursor.to_list(length=5)
            
            print(f"   Retrieved {len(calls)} calls:\n")
            
            for i, call in enumerate(calls, 1):
                print(f"   Call #{i}:")
                print(f"   ├─ _id: {call.get('_id', 'MISSING')}")
                print(f"   ├─ session_id: {call.get('session_id', 'MISSING')}")
                print(f"   ├─ risk_level: {call.get('risk_level', 'MISSING')}")
                print(f"   ├─ risk_score: {call.get('risk_score', 'MISSING')}")
                print(f"   ├─ confidence: {call.get('confidence', 'MISSING')}")
                print(f"   ├─ operator_action: {call.get('operator_action', 'MISSING')}")
                print(f"   ├─ outcome: {call.get('outcome', 'MISSING')}")
                print(f"   ├─ created_at: {call.get('created_at', 'MISSING')}")
                print(f"   ├─ triggered_signals: {call.get('triggered_signals', [])}")
                print(f"   └─ transcript (first 100 chars): {call.get('transcript', 'MISSING')[:100]}...")
                print()
        except Exception as e:
            print(f"   ✗ ERROR fetching calls: {e}\n")
    
    # Step 5: Simulate REST API response
    if count > 0:
        print("STEP 5: Simulating REST API response (GET /calls)...")
        try:
            cursor = db.calls.find().sort("created_at", -1).limit(50)
            calls = await cursor.to_list(length=50)
            
            # Convert ObjectId to string (like the API does)
            for call in calls:
                call["_id"] = str(call["_id"])
            
            response = {
                "calls": calls,
                "total": count,
                "storage": "MongoDB Atlas"
            }
            
            print(f"   Response structure:")
            print(f"   ├─ calls: array of {len(calls)} items")
            print(f"   ├─ total: {count}")
            print(f"   └─ storage: MongoDB Atlas")
            print()
            
            # Save to file for inspection
            with open("debug_api_response.json", "w") as f:
                json.dump(response, f, indent=2, default=str)
            print("   ✓ Saved full response to: debug_api_response.json\n")
            
        except Exception as e:
            print(f"   ✗ ERROR: {e}\n")
    
    # Step 6: Check indexes
    print("STEP 6: Checking database indexes...")
    try:
        indexes = await db.calls.index_information()
        print(f"   Indexes on 'calls' collection:")
        for idx_name, idx_info in indexes.items():
            print(f"   ├─ {idx_name}: {idx_info.get('key', [])}")
        print()
    except Exception as e:
        print(f"   ✗ ERROR: {e}\n")
    
    await close_db()
    
    print("="*60)
    print("DEBUGGING COMPLETE")
    print("="*60)
    print()
    
    # Summary
    print("SUMMARY:")
    if count == 0:
        print("❌ No calls found in database")
        print()
        print("TO FIX:")
        print("1. Make sure backend is running: cd backend && python main.py")
        print("2. Make sure frontend is running: cd frontend && npm run dev")
        print("3. Open http://localhost:5173")
        print("4. Click 'Start Call Transcript' button")
        print("5. Wait 10 seconds for first analysis")
        print("6. Check backend logs for: '✓ Logged to database: ...'")
        print("7. Go to 'Call History' tab in UI")
    else:
        print(f"✅ Found {count} call(s) in database")
        print()
        print("If calls aren't showing in UI:")
        print("1. Check frontend console for errors (F12)")
        print("2. Verify backend is running on port 8000")
        print("3. Check CORS settings in backend/main.py")
        print("4. Try clicking 'Refresh' button in Call History")
        print("5. Check network tab for failed API requests")
    print()


if __name__ == "__main__":
    asyncio.run(debug())
