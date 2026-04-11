"""
Classify background audio to provide situational context.
Example: child crying + questions about shelter = domestic violence risk escalation.
"""

import logging

import librosa
import numpy as np

logger = logging.getLogger(__name__)


def classify_ambient_audio(audio_chunk: np.ndarray, sample_rate: int = 16000) -> dict:
    """
    Classify ambient audio using heuristic frequency-based approach.

    Returns:
    {
        "primary_class": "child_crying",  # or "silence", "traffic", "music", "multiple_speakers"
        "confidence": 0.78,
        "secondary_classes": ["domestic_noise"],
        "risk_relevant": True  # True if class has known risk correlation
    }

    Args:
        audio_chunk: Audio data as numpy array
        sample_rate: Sample rate in Hz

    Returns:
        dict: Classification result with primary_class, confidence, secondary_classes, risk_relevant
    """
    try:
        # Initialize result
        result = {
            "primary_class": "unknown",
            "confidence": 0.0,
            "secondary_classes": [],
            "risk_relevant": False,
        }

        # Calculate RMS energy
        rms = librosa.feature.rms(y=audio_chunk)[0]
        rms_mean = np.mean(rms)
        energy_db = 20 * np.log10(rms_mean) if rms_mean > 0 else -60.0

        # Calculate spectral features
        spec = np.abs(librosa.stft(audio_chunk))
        freqs = librosa.fft_frequencies(sr=sample_rate)

        # Energy in different frequency bands
        low_band = (freqs >= 50) & (freqs < 300)  # 50-300 Hz
        mid_band = (freqs >= 300) & (freqs < 600)  # 300-600 Hz (child crying range)
        high_band = (freqs >= 600) & (freqs < 2000)  # 600-2000 Hz
        very_high_band = freqs >= 2000  # 2000+ Hz

        low_energy = np.mean(spec[low_band, :])
        mid_energy = np.mean(spec[mid_band, :])
        high_energy = np.mean(spec[high_band, :])
        very_high_energy = np.mean(spec[very_high_band, :])

        total_energy = low_energy + mid_energy + high_energy + very_high_energy

        # Normalize band energies
        if total_energy > 0:
            low_ratio = low_energy / total_energy
            mid_ratio = mid_energy / total_energy
            high_ratio = high_energy / total_energy
            very_high_ratio = very_high_energy / total_energy
        else:
            low_ratio = mid_ratio = high_ratio = very_high_ratio = 0.25

        # Classification heuristics

        # 1. Silence: very low energy
        if energy_db < -40:
            result["primary_class"] = "silence"
            result["confidence"] = min(1.0, (-40 - energy_db) / 20)
            result["risk_relevant"] = True  # Isolation indicator

        # 2. Child crying: high energy in 300-600 Hz with bursts
        elif mid_ratio > 0.35 and energy_db > -30:
            # Check for periodic bursts (crying pattern)
            rms_var = np.var(rms)
            if rms_var > 0.01:  # High variance indicates bursts
                result["primary_class"] = "child_crying"
                result["confidence"] = min(1.0, mid_ratio * 2)
                result["risk_relevant"] = True  # Domestic violence indicator

        # 3. Traffic: broadband noise with emphasis on low frequencies
        elif low_ratio > 0.4 and energy_db > -25:
            result["primary_class"] = "traffic"
            result["confidence"] = min(1.0, low_ratio * 1.5)
            result["risk_relevant"] = False  # Not directly risk-relevant

        # 4. Music: harmonic structure (multiple stable pitch peaks)
        elif very_high_ratio > 0.25:
            # Detect harmonic structure using spectral peaks
            spectral_peaks = librosa.util.peak_pick(
                np.mean(spec, axis=1), pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10
            )

            if len(spectral_peaks) > 3:  # Multiple harmonic peaks
                result["primary_class"] = "music"
                result["confidence"] = min(1.0, len(spectral_peaks) / 10)
                result["risk_relevant"] = False

        # 5. Multiple speakers: detect overlapping pitch contours
        else:
            # Use pitch tracking to detect multiple simultaneous speakers
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio_chunk,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
                sr=sample_rate,
            )

            # Check for rapid pitch changes (indicator of multiple speakers)
            f0_voiced = f0[~np.isnan(f0)]
            if len(f0_voiced) > 10:
                pitch_changes = np.abs(np.diff(f0_voiced))
                rapid_changes = np.sum(pitch_changes > 50)  # Changes > 50 Hz

                if rapid_changes > len(f0_voiced) * 0.3:  # 30% of frames have rapid changes
                    result["primary_class"] = "multiple_speakers"
                    result["confidence"] = min(1.0, rapid_changes / len(f0_voiced))
                    result["risk_relevant"] = True  # Argument/conflict indicator

        # Add secondary classes if confidence is moderate
        if result["confidence"] < 0.7 and result["primary_class"] != "unknown":
            # Could be mixed audio
            if mid_ratio > 0.25 and result["primary_class"] != "child_crying":
                result["secondary_classes"].append("domestic_noise")

        logger.debug(
            f"Ambient classification: {result['primary_class']} "
            f"(confidence={result['confidence']:.2f}, "
            f"risk_relevant={result['risk_relevant']})"
        )

        return result

    except Exception as e:
        logger.warning(f"Ambient classification failed: {e}")
        return {
            "primary_class": "unknown",
            "confidence": 0.0,
            "secondary_classes": [],
            "risk_relevant": False,
        }
