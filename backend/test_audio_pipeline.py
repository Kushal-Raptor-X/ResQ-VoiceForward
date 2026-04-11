"""
Test the optimized audio pipeline with backpressure.
This tests the full flow: mic → Sarvam → console output
"""
import asyncio
import logging
import os
import time

from dotenv import load_dotenv

from audio_capture import stream_audio_chunks
from transcriber import transcribe_chunk

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def test_pipeline():
    """Test audio capture → Sarvam transcription with backpressure."""
    
    print("\n" + "="*70)
    print("  🎤 AUDIO PIPELINE TEST (with backpressure)")
    print("="*70)
    
    # Check API key
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        print("\n❌ SARVAM_API_KEY not set in .env")
        return
    
    print(f"\n✅ Sarvam API Key: ...{api_key[-8:]}")
    print("\n📝 Configuration:")
    print(f"   - Chunk duration: 8 seconds")
    print(f"   - Queue size: 1 (strict backpressure)")
    print(f"   - API timeout: 20 seconds")
    print(f"   - Processing: Sequential (no parallel)")
    
    print("\n🎙️  Starting microphone capture...")
    print("   Speak into your microphone. Press Ctrl+C to stop.\n")
    
    chunk_count = 0
    start_time = time.time()
    
    try:
        async for audio_chunk in stream_audio_chunks(source="mic"):
            chunk_count += 1
            elapsed = time.time() - start_time
            
            print(f"\n[Chunk {chunk_count}] Captured 8s audio at {elapsed:.1f}s")
            print(f"[Chunk {chunk_count}] → Sending to Sarvam AI...")
            
            t_start = time.time()
            result = await transcribe_chunk(audio_chunk)
            t_elapsed = time.time() - t_start
            
            if result["text"].strip():
                print(f"[Chunk {chunk_count}] ✓ Transcription ({t_elapsed:.2f}s):")
                print(f"   \"{result['text']}\"")
                print(f"   Language: {result['language']}, Confidence: {result['confidence']:.2f}")
            else:
                print(f"[Chunk {chunk_count}] (no speech detected)")
            
            # Show timing
            print(f"[Chunk {chunk_count}] ⏱ Sarvam latency: {t_elapsed:.2f}s")
            
            if chunk_count >= 3:
                print("\n✅ Test complete (3 chunks processed)")
                break
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_pipeline())
