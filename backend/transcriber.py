"""
Transcription pipeline.
Phase 1: Mock transcription cycling through demo scenarios.
Phase 4: Replace with faster-whisper + sounddevice.
"""
import asyncio

from mock_data import DEMO_SCENARIOS, SEGMENT_ANALYSES

LINE_DELAY = 3.0
SEGMENT_DELAY = 2.0


async def start_mock_transcription(emit_line_callback, emit_analysis_callback=None):
    """
    Streams the demo scenario line by line.
    Emits a pre-computed segment analysis after each segment completes.
    """
    for segment_idx, segment in enumerate(DEMO_SCENARIOS):
        for line in segment:
            await emit_line_callback(line)
            await asyncio.sleep(LINE_DELAY)

        if emit_analysis_callback and segment_idx < len(SEGMENT_ANALYSES):
            await emit_analysis_callback(SEGMENT_ANALYSES[segment_idx])

        await asyncio.sleep(SEGMENT_DELAY)

    while True:
        await asyncio.sleep(60)
