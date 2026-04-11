#!/usr/bin/env python3
"""
Check Sarvam AI API status and connectivity.
Helps diagnose timeout issues.
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv
import time

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"

async def check_api_status():
    print("\n" + "="*70)
    print("  🔍 SARVAM AI API STATUS CHECK")
    print("="*70)
    
    # Check API key
    if not SARVAM_API_KEY:
        print("\n❌ SARVAM_API_KEY not found in .env")
        return
    
    print(f"\n✅ API Key: ...{SARVAM_API_KEY[-8:]}")
    print(f"📍 API URL: {SARVAM_API_URL}")
    
    # Test connectivity
    print("\n" + "="*70)
    print("Testing connectivity...")
    print("="*70)
    
    # Test 1: Basic HTTP connection
    print("\n1️⃣  Testing basic HTTP connection...")
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.head("https://api.sarvam.ai") as resp:
                print(f"   ✅ HTTP connection OK (status: {resp.status})")
    except asyncio.TimeoutError:
        print("   ❌ Connection timeout (5s)")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
    
    # Test 2: API endpoint with empty request
    print("\n2️⃣  Testing API endpoint...")
    try:
        timeout = aiohttp.ClientTimeout(total=15, connect=5, sock_read=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            form = aiohttp.FormData()
            form.add_field('file', b'', filename='test.wav', content_type='audio/wav')
            form.add_field('language_code', 'auto')
            form.add_field('model', 'saaras:v2.5')
            
            headers = {"Authorization": f"Bearer {SARVAM_API_KEY}"}
            
            t_start = time.time()
            async with session.post(SARVAM_API_URL, data=form, headers=headers) as resp:
                t_end = time.time()
                print(f"   ✅ API responded in {t_end - t_start:.2f}s (status: {resp.status})")
                
                if resp.status != 200:
                    text = await resp.text()
                    print(f"   ℹ️  Response: {text[:100]}")
    
    except asyncio.TimeoutError as e:
        print(f"   ❌ API timeout: {e}")
        print("   💡 Sarvam API may be slow or overloaded")
        print("   💡 Try again in a few minutes")
    except Exception as e:
        print(f"   ❌ API error: {e}")
    
    # Test 3: Network diagnostics
    print("\n3️⃣  Network diagnostics...")
    try:
        import socket
        print("   Testing DNS resolution...")
        ip = socket.gethostbyname("api.sarvam.ai")
        print(f"   ✅ DNS resolved: api.sarvam.ai → {ip}")
    except Exception as e:
        print(f"   ❌ DNS resolution failed: {e}")
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS:")
    print("="*70)
    print("""
If you're getting timeouts:

1. Check your internet connection
   - Try: ping google.com
   - Try: curl https://api.sarvam.ai

2. Sarvam API may be slow
   - Increase timeout in transcriber.py (already done: 30s)
   - Try again in a few minutes
   - Check Sarvam status page

3. Use mock transcription as fallback
   - Set: USE_MOCK_TRANSCRIPTION="true" in .env
   - This will use hardcoded transcript instead

4. Check firewall/proxy
   - Some networks block API calls
   - Try from a different network
   - Check corporate firewall settings
""")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(check_api_status())
