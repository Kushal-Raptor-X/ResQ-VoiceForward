"""
Quick test to check if the backend is running and responding.
"""
import requests

try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print("✅ Backend is running!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Backend returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Backend is NOT running!")
    print("   Start it with: python backend/main.py")
except Exception as e:
    print(f"❌ Error: {e}")
