"""
Extract paralinguistic features from audio that indicate emotional state.
These features augment the text transcript for risk analysis.
"""

import logging
from typing import Optional

import librosa
import numpy as np

logger = logging.getLogger(__name__)


def extract_prosody_features(audio_chunk: np.ndarray, sample_rate: int = 16000) -> dict:
    """
    Extract prosody features from audio chunk.

    Returns:
    {
        "speaking_rate_wpm": 120,      # words per minute (estimate from syllable rate)
        "pitch_mean_hz": 180.5,        # average fundamental frequency
        "pitch_variance": 45.2,        # emotional variation indicator
        "energy_db": -12.3,            # loudness (RMS in dB)
        "pause_ratio": 0.35,           # % of chunk that is silence
        "pitch_trend": "falling",      # "rising" | "falling" | "stable"
        "unusual_calm": False          # critical risk indicator
    }

    Args:
        audio_chunk: Audio data as numpy array, shape (n_samples,), dtype float32
        sample_rate: Sample rate in Hz

    Returns:
        dict: Prosody features with all fields populated or None on failure
    """
    try:
        # Initialize result dict
        result = {
            "speaking_rate_wpm": None,
            "pitch_mean_hz": None,
            "pitch_variance": None,
            "energy_db": None,
            "pause_ratio": None,
            "pitch_trend": "unknown",
            "unusual_calm": False,
        }

        # 1. Extract pitch (F0) using librosa.pyin
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio_chunk,
            fmin=librosa.note_to_hz("C2"),  # 65 Hz (low male voice)
            fmax=librosa.note_to_hz("C7"),  # 2093 Hz (high female voice)
            sr=sample_rate,
        )

        # Filter out unvoiced frames (NaN values)
        f0_voiced = f0[~np.isnan(f0)]

        if len(f0_voiced) > 0:
            result["pitch_mean_hz"] = float(np.mean(f0_voiced))
            result["pitch_variance"] = float(np.var(f0_voiced))

            # Pitch trend: linear regression on f0 values
            if len(f0_voiced) > 5:
                x = np.arange(len(f0_voiced))
                slope = np.polyfit(x, f0_voiced, 1)[0]
                # Slope in Hz per frame, convert to Hz per second
                slope_per_sec = slope * (sample_rate / len(audio_chunk)) * len(f0_voiced)

                if slope_per_sec > 5:
                    result["pitch_trend"] = "rising"
                elif slope_per_sec < -5:
                    result["pitch_trend"] = "falling"
                else:
                    result["pitch_trend"] = "stable"

        # 2. Extract energy (RMS) and convert to dB
        rms = librosa.feature.rms(y=audio_chunk)[0]
        rms_mean = np.mean(rms)

        if rms_mean > 0:
            result["energy_db"] = float(20 * np.log10(rms_mean))
        else:
            result["energy_db"] = -60.0  # Very quiet

        # 3. Calculate pause ratio using VAD
        # Use librosa.effects.split to find non-silent intervals
        non_silent_intervals = librosa.effects.split(audio_chunk, top_db=30)

        if len(non_silent_intervals) > 0:
            non_silent_samples = sum(end - start for start, end in non_silent_intervals)
            result["pause_ratio"] = float(1.0 - (non_silent_samples / len(audio_chunk)))
        else:
            result["pause_ratio"] = 1.0  # All silence

        # 4. Estimate speaking rate from syllable onset detection
        # Use onset detection as proxy for syllables
        onset_frames = librosa.onset.onset_detect(
            y=audio_chunk, sr=sample_rate, units="frames"
        )

        if len(onset_frames) > 0:
            # Approximate: syllables per second * 60 / 1.5 ≈ words per minute
            # (assuming ~1.5 syllables per word on average)
            duration_sec = len(audio_chunk) / sample_rate
            syllables_per_sec = len(onset_frames) / duration_sec
            result["speaking_rate_wpm"] = float((syllables_per_sec * 60) / 1.5)
        else:
            result["speaking_rate_wpm"] = 0.0

        # 5. Detect unusual calm pattern
        # Heuristic: energy < -15dB AND pitch_variance < 20 AND speaking_rate < 100 wpm
        if (
            result["energy_db"] is not None
            and result["pitch_variance"] is not None
            and result["speaking_rate_wpm"] is not None
        ):
            if (
                result["energy_db"] < -15
                and result["pitch_variance"] < 20
                and result["speaking_rate_wpm"] < 100
            ):
                result["unusual_calm"] = True
                logger.warning(
                    f"UNUSUAL CALM DETECTED: energy={result['energy_db']:.1f}dB, "
                    f"pitch_var={result['pitch_variance']:.1f}Hz, "
                    f"rate={result['speaking_rate_wpm']:.0f}wpm"
                )

        return result

    except Exception as e:
        logger.warning(f"Prosody extraction failed: {e}")
        # Return dict with all None values
        return {
            "speaking_rate_wpm": None,
            "pitch_mean_hz": None,
            "pitch_variance": None,
            "energy_db": None,
            "pause_ratio": None,
            "pitch_trend": "unknown",
            "unusual_calm": False,
        }
