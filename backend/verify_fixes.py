"""
Verify that the audio queue overflow fixes are in place.
This script checks the code without running the full pipeline.
"""
import os
import re

print("\n" + "="*70)
print("  🔍 VERIFYING AUDIO QUEUE OVERFLOW FIXES")
print("="*70)

checks_passed = 0
checks_total = 0

# Check 1: Chunk duration increased to 8s
checks_total += 1
with open("audio_capture.py", "r") as f:
    content = f.read()
    if "chunk_duration_sec: float = 8.0" in content:
        print("\n✅ Check 1: Chunk duration increased to 8.0 seconds")
        checks_passed += 1
    else:
        print("\n❌ Check 1: Chunk duration NOT set to 8.0 seconds")

# Check 2: Queue size reduced to 1
checks_total += 1
if "asyncio.Queue(maxsize=1)" in content:
    print("✅ Check 2: Queue size reduced to 1 (strict backpressure)")
    checks_passed += 1
else:
    print("❌ Check 2: Queue size NOT set to 1")

# Check 3: Non-blocking put_nowait
checks_total += 1
if "put_nowait" in content:
    print("✅ Check 3: Using put_nowait() for non-blocking queue operations")
    checks_passed += 1
else:
    print("❌ Check 3: NOT using put_nowait()")

# Check 4: Backpressure logging
checks_total += 1
if "backpressure enabled" in content:
    print("✅ Check 4: Backpressure logging added")
    checks_passed += 1
else:
    print("❌ Check 4: Backpressure logging NOT added")

# Check 5: Sarvam timeout reduced
checks_total += 1
with open("transcriber.py", "r") as f:
    content = f.read()
    if "total=20" in content:
        print("✅ Check 5: Sarvam API timeout reduced to 20 seconds")
        checks_passed += 1
    else:
        print("❌ Check 5: Sarvam API timeout NOT set to 20 seconds")

# Check 6: Retries reduced
checks_total += 1
if "max_retries: int = 1" in content:
    print("✅ Check 6: Max retries reduced to 1 (fail fast)")
    checks_passed += 1
else:
    print("❌ Check 6: Max retries NOT set to 1")

# Check 7: Mock transcription removed from .env
checks_total += 1
with open(".env", "r") as f:
    content = f.read()
    if "USE_MOCK_TRANSCRIPTION" not in content:
        print("✅ Check 7: Mock transcription flag removed from .env")
        checks_passed += 1
    else:
        print("❌ Check 7: Mock transcription flag still in .env")

# Check 8: Sequential processing in main.py
checks_total += 1
try:
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "Sequential processing with backpressure" in content:
            print("✅ Check 8: Sequential processing implemented in main.py")
            checks_passed += 1
        else:
            print("❌ Check 8: Sequential processing NOT implemented")
    
    # Check 9: Mock mode removed from main.py
    checks_total += 1
    if "use_mock = os.getenv" not in content:
        print("✅ Check 9: Mock transcription mode removed from main.py")
        checks_passed += 1
    else:
        print("❌ Check 9: Mock transcription mode still in main.py")
except Exception as e:
    print(f"❌ Check 8-9: Error reading main.py: {e}")
    checks_total += 1

# Summary
print("\n" + "="*70)
print(f"  RESULTS: {checks_passed}/{checks_total} checks passed")
print("="*70)

if checks_passed == checks_total:
    print("\n🎉 All fixes verified! Audio queue overflow should be resolved.")
    print("\n📝 Expected behavior:")
    print("   - Audio captured in 8-second chunks")
    print("   - Sarvam API processes sequentially (15-30s per chunk)")
    print("   - Queue never overflows (size=1, backpressure enabled)")
    print("   - Some chunks dropped while processing (this is normal)")
    print("\n🚀 Ready to test with: python main.py")
else:
    print(f"\n⚠️  {checks_total - checks_passed} checks failed. Review the code.")

print()
