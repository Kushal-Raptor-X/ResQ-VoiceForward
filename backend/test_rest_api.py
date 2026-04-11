"""
test_rest_api.py — Test REST API endpoints for call history.
"""
import asyncio

import aiohttp


async def test_api():
    """Test the REST API endpoints."""
    print("\n=== Testing REST API Endpoints ===\n")
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("1. Testing /health endpoint...")
        try:
            async with session.get(f"{base_url}/health") as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Response: {data}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            print("   Make sure backend is running: python main.py")
            return
        
        # Test db-status endpoint
        print("\n2. Testing /db-status endpoint...")
        try:
            async with session.get(f"{base_url}/db-status") as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Connected: {data.get('connected')}")
                print(f"   Storage: {data.get('storage')}")
                print(f"   Total calls: {data.get('total_calls_logged', 'N/A')}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        # Test GET /calls endpoint
        print("\n3. Testing GET /calls endpoint...")
        try:
            async with session.get(f"{base_url}/calls?limit=10") as resp:
                data = await resp.json()
                print(f"   Status: {resp.status}")
                print(f"   Storage: {data.get('storage')}")
                print(f"   Total calls: {data.get('total')}")
                print(f"   Returned: {len(data.get('calls', []))} calls")
                
                if data.get('calls'):
                    print(f"\n   Recent calls:")
                    for i, call in enumerate(data['calls'][:3], 1):
                        print(f"   {i}. Session: {call.get('session_id', 'N/A')}")
                        print(f"      Risk: {call.get('risk_level', 'N/A')} ({call.get('risk_score', 0)}/100)")
                        print(f"      Confidence: {call.get('confidence', 'N/A')}")
                        print(f"      Created: {call.get('created_at', 'N/A')}")
                        print()
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("=== Test Complete ===\n")


if __name__ == "__main__":
    asyncio.run(test_api())
