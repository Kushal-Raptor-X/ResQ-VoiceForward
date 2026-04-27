"""
Audio capture from microphone or file with configurable chunk size.
Supports:
- Live microphone input via sounddevice
- Fallback to pre-recorded .wav file for demo
- 16kHz sample rate, mono channel (Whisper requirement)
- Yield audio chunks every 3-5 seconds as numpy arrays
"""

import asyncio
import logging
from pathlib import Path
from typing import AsyncIterator

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

logger = logging.getLogger(__name__)


async def stream_audio_chunks(
    source: str = "mic",  # "mic" or path to .wav file
    chunk_duration_sec: float = 4.0,  # 4 seconds - faster chunks for responsive demo
    sample_rate: int = 16000,
) -> AsyncIterator[np.ndarray]:
    """
    Yield audio chunks as numpy arrays.

    For "mic": use sounddevice.InputStream with callback buffering
    For file path: load with scipy.io.wavfile, slice into chunks, yield with asyncio.sleep

    Each chunk: shape (sample_rate * chunk_duration_sec,), dtype float32, range [-1, 1]

    Args:
        source: "mic" for microphone or path to .wav file
        chunk_duration_sec: Duration of each audio chunk in seconds
        sample_rate: Sample rate in Hz (16000 for Whisper)

    Yields:
        np.ndarray: Audio chunk with shape (sample_rate * chunk_duration_sec,),
                    dtype float32, range [-1, 1]

    Raises:
        FileNotFoundError: If source file doesn't exist
        sd.PortAudioError: If microphone access denied (triggers fallback)
    """
    if source == "mic":
        # Microphone mode
        try:
            logger.info("Initializing microphone capture...")
            async for chunk in _stream_from_microphone(chunk_duration_sec, sample_rate):
                yield chunk
        except sd.PortAudioError as e:
            logger.error(f"Microphone access denied: {e}")
            logger.info("Falling back to demo audio file")
            # Fallback to demo file
            demo_path = "backend/demo_audio/demo.wav"
            if Path(demo_path).exists():
                async for chunk in _stream_from_file(demo_path, chunk_duration_sec, sample_rate):
                    yield chunk
            else:
                logger.error(f"Demo file not found at {demo_path}")
                raise FileNotFoundError(f"Demo file not found: {demo_path}")
    else:
        # File mode
        if not Path(source).exists():
            raise FileNotFoundError(f"Audio file not found: {source}")

        logger.info(f"Streaming audio from file: {source}")
        async for chunk in _stream_from_file(source, chunk_duration_sec, sample_rate):
            yield chunk


async def _stream_from_microphone(
    chunk_duration_sec: float, sample_rate: int
) -> AsyncIterator[np.ndarray]:
    """
    Stream audio from microphone using sounddevice.

    Uses callback with asyncio.Queue to bridge callback thread → async generator.
    Implements backpressure: only captures new audio when previous chunk is consumed.
    """
    audio_queue: asyncio.Queue = asyncio.Queue(maxsize=1)  # Only 1 chunk at a time - strict backpressure
    chunk_size = int(sample_rate * chunk_duration_sec)

    def audio_callback(indata, frames, time_info, status):
        """Callback called by sounddevice in separate thread."""
        if status:
            logger.warning(f"Audio callback status: {status}")

        # Convert to float32 and flatten
        audio_data = indata.copy().flatten().astype(np.float32)

        # Non-blocking put - if queue is full, drop the chunk
        # This prevents blocking the audio thread
        try:
            audio_queue.put_nowait(audio_data)
        except asyncio.QueueFull:
            # This is expected when Sarvam is processing - just skip this chunk
            pass

    # Open input stream
    stream = sd.InputStream(
        samplerate=sample_rate,
        channels=1,  # Mono
        dtype=np.float32,
        blocksize=chunk_size,
        callback=audio_callback,
    )

    with stream:
        logger.info(f"Microphone stream started (chunk_duration={chunk_duration_sec}s, backpressure enabled)")
        while True:
            chunk = await audio_queue.get()
            yield chunk


async def _stream_from_file(
    file_path: str, chunk_duration_sec: float, sample_rate: int
) -> AsyncIterator[np.ndarray]:
    """
    Stream audio from file with 50% overlap and continuous looping.

    Args:
        file_path: Path to .wav file
        chunk_duration_sec: Duration of each chunk
        sample_rate: Target sample rate (will resample if needed)

    Yields:
        Audio chunks with 50% overlap, loops continuously when file ends
    """
    # Load audio file
    file_sample_rate, audio_data = wavfile.read(file_path)

    # Convert to float32 and normalize to [-1, 1]
    if audio_data.dtype == np.int16:
        audio_data = audio_data.astype(np.float32) / 32768.0
    elif audio_data.dtype == np.int32:
        audio_data = audio_data.astype(np.float32) / 2147483648.0
    elif audio_data.dtype == np.uint8:
        audio_data = (audio_data.astype(np.float32) - 128) / 128.0
    else:
        audio_data = audio_data.astype(np.float32)

    # Convert stereo to mono if needed
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)

    # Resample if needed
    if file_sample_rate != sample_rate:
        logger.info(f"Resampling from {file_sample_rate}Hz to {sample_rate}Hz")
        # Simple resampling (for production, use librosa.resample)
        duration = len(audio_data) / file_sample_rate
        new_length = int(duration * sample_rate)
        audio_data = np.interp(
            np.linspace(0, len(audio_data), new_length),
            np.arange(len(audio_data)),
            audio_data,
        )

    chunk_size = int(sample_rate * chunk_duration_sec)
    hop_size = chunk_size  # No overlap — sequential chunks

    logger.info(
        f"File loaded: duration={len(audio_data)/sample_rate:.2f}s, "
        f"chunk_size={chunk_size}, hop_size={hop_size}"
    )

    # Stream chunks sequentially (no overlap)
    position = 0
    while True:
        # Extract chunk
        chunk = audio_data[position : position + chunk_size]

        # If chunk is too short (end of file), pad with zeros and restart
        if len(chunk) < chunk_size:
            logger.info("Reached end of file, looping...")
            chunk = np.pad(chunk, (0, chunk_size - len(chunk)), mode="constant")
            position = 0  # Restart from beginning
        else:
            position += hop_size

        yield chunk

        # Simulate real-time playback (5 seconds per chunk)
        await asyncio.sleep(chunk_duration_sec)
