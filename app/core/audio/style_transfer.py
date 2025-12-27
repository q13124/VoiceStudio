"""
Style Transfer Module for VoiceStudio
Voice style transfer and prosody conversion

Compatible with:
- Python 3.10+
- librosa>=0.11.0
- scipy>=1.9.0
- numpy>=1.26.0
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)

try:
    import librosa

    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False
    logger.warning("librosa not installed. Install with: pip install librosa")

try:
    from scipy import signal

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.warning("scipy not installed. Install with: pip install scipy")

try:
    import soundfile as sf

    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False
    logger.warning("soundfile not installed. Install with: pip install soundfile")

# Import audio utilities
try:
    from .audio_utils import (
        analyze_voice_characteristics,
        load_audio,
        match_voice_profile,
    )

    HAS_AUDIO_UTILS = True
except ImportError:
    HAS_AUDIO_UTILS = False
    logger.warning("audio_utils not available")

# Import speaker encoder for style embedding (optional)
HAS_SPEAKER_ENCODER = False
try:
    from ..engines.speaker_encoder_engine import SpeakerEncoderEngine

    HAS_SPEAKER_ENCODER = True
except (ImportError, AttributeError, Exception):
    HAS_SPEAKER_ENCODER = False


class StyleTransfer:
    """
    Style Transfer for voice prosody and style conversion.

    Supports:
    - Prosody transfer (pitch, rhythm, energy)
    - Emotion transfer
    - Accent transfer
    - Style intensity control
    - Reference-based style extraction
    """

    def __init__(self, sample_rate: int = 24000):
        """
        Initialize Style Transfer.

        Args:
            sample_rate: Default sample rate for processing
        """
        self.sample_rate = sample_rate
        self.speaker_encoder = None

    def transfer_style(
        self,
        source_audio: Union[str, Path, np.ndarray],
        style_reference: Union[str, Path, np.ndarray],
        sample_rate: Optional[int] = None,
        transfer_strength: float = 0.8,
        preserve_content: bool = True,
        preserve_emotion: bool = False,
        **kwargs,
    ) -> np.ndarray:
        """
        Transfer style from reference to source audio.

        Args:
            source_audio: Source audio to modify
            style_reference: Reference audio with target style
            sample_rate: Sample rate (uses instance default if None)
            transfer_strength: Style transfer strength (0.0 to 1.0)
            preserve_content: Preserve linguistic content
            preserve_emotion: Preserve emotional characteristics
            **kwargs: Additional transfer parameters

        Returns:
            Style-transferred audio array
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        # Load audio if paths provided
        if isinstance(source_audio, (str, Path)):
            source, src_sr = load_audio(str(source_audio))
            if sample_rate != src_sr:
                if HAS_LIBROSA:
                    source = librosa.resample(
                        source, orig_sr=src_sr, target_sr=sample_rate
                    )
        else:
            source = source_audio

        if isinstance(style_reference, (str, Path)):
            reference, ref_sr = load_audio(str(style_reference))
            if sample_rate != ref_sr:
                if HAS_LIBROSA:
                    reference = librosa.resample(
                        reference, orig_sr=ref_sr, target_sr=sample_rate
                    )
        else:
            reference = style_reference

        # Convert to mono if needed
        if len(source.shape) > 1:
            source = np.mean(source, axis=1)
        if len(reference.shape) > 1:
            reference = np.mean(reference, axis=1)

        # Extract style characteristics from reference
        style_features = self.extract_style_features(reference, sample_rate)

        # Apply style transfer
        transferred = self.apply_style_transfer(
            source,
            style_features,
            sample_rate,
            transfer_strength,
            preserve_content,
            preserve_emotion,
            **kwargs,
        )

        return transferred

    def extract_style_features(self, audio: np.ndarray, sample_rate: int) -> Dict:
        """
        Extract style features from audio.

        Args:
            audio: Input audio array
            sample_rate: Sample rate

        Returns:
            Dictionary of style features
        """
        features = {}

        if not HAS_LIBROSA:
            logger.warning("librosa required for style feature extraction")
            return features

        try:
            # Extract fundamental frequency (F0)
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
            )

            f0_voiced = f0[voiced_flag]
            if len(f0_voiced) > 0:
                features["f0_mean"] = float(np.nanmean(f0_voiced))
                features["f0_std"] = float(np.nanstd(f0_voiced))
                features["f0_range"] = float(
                    np.nanmax(f0_voiced) - np.nanmin(f0_voiced)
                )

            # Extract tempo (speaking rate)
            tempo, beats = librosa.beat.beat_track(
                y=audio, sr=sample_rate, units="time"
            )
            features["tempo"] = float(tempo)

            # Extract energy envelope
            frame_length = 2048
            hop_length = 512
            rms = librosa.feature.rms(
                y=audio, frame_length=frame_length, hop_length=hop_length
            )[0]
            features["energy_mean"] = float(np.mean(rms))
            features["energy_std"] = float(np.std(rms))
            features["energy_range"] = float(np.max(rms) - np.min(rms))

            # Extract spectral features
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio, sr=sample_rate
            )[0]
            features["spectral_centroid_mean"] = float(np.mean(spectral_centroid))

            # Extract zero-crossing rate (speech-like characteristics)
            zcr = librosa.feature.zero_crossing_rate(audio)[0]
            features["zcr_mean"] = float(np.mean(zcr))

        except Exception as e:
            logger.warning(f"Style feature extraction failed: {e}")

        return features

    def apply_style_transfer(
        self,
        source_audio: np.ndarray,
        style_features: Dict,
        sample_rate: int,
        transfer_strength: float,
        preserve_content: bool,
        preserve_emotion: bool,
        **kwargs,
    ) -> np.ndarray:
        """
        Apply style transfer to source audio.

        Args:
            source_audio: Source audio to modify
            style_features: Style features from reference
            sample_rate: Sample rate
            transfer_strength: Transfer strength (0.0 to 1.0)
            preserve_content: Preserve linguistic content
            preserve_emotion: Preserve emotional characteristics
            **kwargs: Additional parameters

        Returns:
            Style-transferred audio
        """
        if not HAS_LIBROSA:
            logger.warning("librosa required for style transfer")
            return source_audio

        transferred = source_audio.copy()

        # Extract source features
        source_features = self.extract_style_features(source_audio, sample_rate)

        # Transfer pitch (F0)
        if "f0_mean" in style_features and "f0_mean" in source_features:
            target_f0 = style_features["f0_mean"]
            source_f0 = source_features["f0_mean"]

            if source_f0 > 0 and target_f0 > 0:
                pitch_shift_semitones = (
                    np.log2(target_f0 / source_f0) * 12.0 * transfer_strength
                )

                # Limit pitch shift range
                pitch_shift_semitones = max(-12.0, min(12.0, pitch_shift_semitones))

                if abs(pitch_shift_semitones) > 0.1:
                    try:
                        transferred = librosa.effects.pitch_shift(
                            transferred,
                            sr=sample_rate,
                            n_steps=pitch_shift_semitones,
                        )
                    except Exception as e:
                        logger.warning(f"Pitch shift failed: {e}")

        # Transfer tempo (speaking rate)
        if "tempo" in style_features and "tempo" in source_features:
            target_tempo = style_features["tempo"]
            source_tempo = source_features["tempo"]

            if source_tempo > 0 and target_tempo > 0:
                tempo_ratio = (target_tempo / source_tempo) * transfer_strength + (
                    1.0 - transfer_strength
                )

                # Limit tempo ratio
                tempo_ratio = max(0.5, min(2.0, tempo_ratio))

                if abs(tempo_ratio - 1.0) > 0.05:
                    try:
                        transferred = librosa.effects.time_stretch(
                            transferred, rate=tempo_ratio
                        )
                    except Exception as e:
                        logger.warning(f"Tempo change failed: {e}")

        # Transfer energy envelope
        if "energy_mean" in style_features and "energy_mean" in source_features:
            target_energy = style_features["energy_mean"]
            source_energy = source_features["energy_mean"]

            if source_energy > 0:
                energy_ratio = (target_energy / source_energy) * transfer_strength + (
                    1.0 - transfer_strength
                )

                # Limit energy ratio
                energy_ratio = max(0.1, min(3.0, energy_ratio))

                transferred = transferred * energy_ratio

        # Normalize to prevent clipping
        max_val = np.max(np.abs(transferred))
        if max_val > 0:
            transferred = transferred / max_val * 0.95

        return transferred

    def transfer_emotion(
        self,
        audio: np.ndarray,
        sample_rate: int,
        target_emotion: str,
        intensity: float = 0.7,
    ) -> np.ndarray:
        """
        Transfer emotion to audio.

        Args:
            audio: Input audio array
            sample_rate: Sample rate
            target_emotion: Target emotion ('happy', 'sad', 'angry', etc.)
            intensity: Emotion intensity (0.0 to 1.0)

        Returns:
            Emotion-transferred audio
        """
        if not HAS_LIBROSA:
            logger.warning("librosa required for emotion transfer")
            return audio

        emotion_params = {
            "happy": {"pitch_shift": 2.0, "tempo": 1.1, "energy": 1.2},
            "sad": {"pitch_shift": -2.0, "tempo": 0.9, "energy": 0.8},
            "angry": {"pitch_shift": 1.0, "tempo": 1.15, "energy": 1.3},
            "excited": {"pitch_shift": 3.0, "tempo": 1.2, "energy": 1.4},
            "calm": {"pitch_shift": -1.0, "tempo": 0.95, "energy": 0.9},
            "neutral": {"pitch_shift": 0.0, "tempo": 1.0, "energy": 1.0},
        }

        params = emotion_params.get(target_emotion.lower(), emotion_params["neutral"])

        transferred = audio.copy()

        # Apply pitch shift
        if params["pitch_shift"] != 0:
            pitch_shift = params["pitch_shift"] * intensity
            pitch_shift = max(-12.0, min(12.0, pitch_shift))
            try:
                transferred = librosa.effects.pitch_shift(
                    transferred, sr=sample_rate, n_steps=pitch_shift
                )
            except Exception as e:
                logger.warning(f"Pitch shift failed: {e}")

        # Apply tempo change
        if params["tempo"] != 1.0:
            tempo = params["tempo"] * intensity + (1.0 - intensity)
            tempo = max(0.5, min(2.0, tempo))
            try:
                transferred = librosa.effects.time_stretch(transferred, rate=tempo)
            except Exception as e:
                logger.warning(f"Tempo change failed: {e}")

        # Apply energy change
        if params["energy"] != 1.0:
            energy = params["energy"] * intensity + (1.0 - intensity)
            energy = max(0.1, min(3.0, energy))
            transferred = transferred * energy

        # Normalize
        max_val = np.max(np.abs(transferred))
        if max_val > 0:
            transferred = transferred / max_val * 0.95

        return transferred

    def transfer_accent(
        self,
        audio: np.ndarray,
        sample_rate: int,
        target_accent: str,
        intensity: float = 0.7,
    ) -> np.ndarray:
        """
        Transfer accent to audio.

        Args:
            audio: Input audio array
            sample_rate: Sample rate
            target_accent: Target accent ('american', 'british', etc.)
            intensity: Accent intensity (0.0 to 1.0)

        Returns:
            Accent-transferred audio
        """
        if not HAS_LIBROSA:
            logger.warning("librosa required for accent transfer")
            return audio

        accent_params = {
            "american": {"pitch_shift": 0, "tempo": 1.0, "formant_shift": 0},
            "british": {"pitch_shift": -0.5, "tempo": 0.95, "formant_shift": -0.1},
            "australian": {"pitch_shift": 0.3, "tempo": 1.05, "formant_shift": 0.1},
            "indian": {"pitch_shift": 0.5, "tempo": 1.1, "formant_shift": 0.2},
            "neutral": {"pitch_shift": 0, "tempo": 1.0, "formant_shift": 0},
        }

        params = accent_params.get(target_accent.lower(), accent_params["neutral"])

        transferred = audio.copy()

        # Apply pitch shift
        if params["pitch_shift"] != 0:
            pitch_shift = params["pitch_shift"] * intensity * 12
            pitch_shift = max(-12.0, min(12.0, pitch_shift))
            try:
                transferred = librosa.effects.pitch_shift(
                    transferred, sr=sample_rate, n_steps=pitch_shift
                )
            except Exception as e:
                logger.warning(f"Pitch shift failed: {e}")

        # Apply tempo change
        if params["tempo"] != 1.0:
            tempo = params["tempo"] * intensity + (1.0 - intensity)
            tempo = max(0.5, min(2.0, tempo))
            try:
                transferred = librosa.effects.time_stretch(transferred, rate=tempo)
            except Exception as e:
                logger.warning(f"Tempo change failed: {e}")

        # Apply formant shift (simplified via spectral modification)
        if params["formant_shift"] != 0:
            formant_shift = params["formant_shift"] * intensity
            try:
                stft = librosa.stft(transferred)
                stft_shifted = librosa.phase_vocoder(stft, rate=1.0 + formant_shift)
                transferred = librosa.istft(stft_shifted)
            except Exception as e:
                logger.warning(f"Formant shift failed: {e}")

        # Normalize
        max_val = np.max(np.abs(transferred))
        if max_val > 0:
            transferred = transferred / max_val * 0.95

        return transferred


def create_style_transfer(sample_rate: int = 24000) -> StyleTransfer:
    """
    Factory function to create a Style Transfer instance.

    Args:
        sample_rate: Default sample rate for processing

    Returns:
        Initialized StyleTransfer instance
    """
    return StyleTransfer(sample_rate=sample_rate)


def transfer_voice_style(
    source_audio: Union[str, Path, np.ndarray],
    style_reference: Union[str, Path, np.ndarray],
    sample_rate: int = 24000,
    transfer_strength: float = 0.8,
    **kwargs,
) -> np.ndarray:
    """
    Convenience function to transfer voice style.

    Args:
        source_audio: Source audio to modify
        style_reference: Reference audio with target style
        sample_rate: Sample rate
        transfer_strength: Style transfer strength (0.0 to 1.0)
        **kwargs: Additional transfer parameters

    Returns:
        Style-transferred audio array
    """
    transfer = StyleTransfer(sample_rate=sample_rate)
    return transfer.transfer_style(
        source_audio, style_reference, sample_rate, transfer_strength, **kwargs
    )
