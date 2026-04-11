# Replace with faster-whisper in Phase 4
import asyncio

from mock_data import MOCK_TRANSCRIPT


async def start_mock_transcription(emit_callback):
    while True:
        for line in MOCK_TRANSCRIPT:
            await emit_callback(line)
            await asyncio.sleep(3)
