"""
Voice Profile Management Routes

CRUD operations for voice profiles.
"""

import logging
import time
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..error_handling import ErrorCodes
from ..exceptions import ProfileNotFoundException
from ..models import ApiOk
from ..models_additional import (
    ReferenceAudioPreprocessRequest,
    ReferenceAudioPreprocessResponse,
)
from ..optimization import PaginationParams, cache_response, get_pagination_params

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


class VoiceProfile(BaseModel):
    id: str
    name: str
    language: str = "en"
    emotion: Optional[str] = None
    quality_score: float = 0.0
    tags: List[str] = []
    reference_audio_url: Optional[str] = None


class ProfileCreateRequest(BaseModel):
    name: str
    language: str = "en"
    emotion: Optional[str] = None
    tags: List[str] = []


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    emotion: Optional[str] = None
    tags: Optional[List[str]] = None


# In-memory storage (replace with database in production)
_profiles: dict[str, VoiceProfile] = {}
_MAX_PROFILES = 1000  # Maximum number of profiles
_profile_timestamps: dict[str, float] = {}  # profile_id -> creation_time


def _cleanup_old_profiles():
    """
    Clean up old profiles from storage to prevent memory accumulation.

    Removes profiles beyond MAX_PROFILES (oldest first based on creation time).
    """
    if len(_profiles) > _MAX_PROFILES:
        # Sort by creation time (oldest first)
        sorted_profiles = sorted(
            _profile_timestamps.items(),
            key=lambda x: x[1],
        )
        excess = len(_profiles) - _MAX_PROFILES
        for profile_id, _ in sorted_profiles[:excess]:
            if profile_id in _profiles:
                del _profiles[profile_id]
            if profile_id in _profile_timestamps:
                del _profile_timestamps[profile_id]
        logger.info(f"Cleaned up {excess} old profiles from storage")


@router.get(
    "",
    summary="List voice profiles",
    description="""
    Retrieve a paginated list of all voice profiles.
    
    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 50, max: 1000)
    
    **Response:**
    Returns a paginated list of voice profiles with metadata.
    
    **Example:**
    ```json
    {
      "items": [
        {
          "id": "profile_123",
          "name": "John Doe Voice",
          "language": "en",
          "quality_score": 4.5
        }
      ],
      "total": 1,
      "page": 1,
      "page_size": 50
    }
    ```
    """,
    responses={
        200: {
            "description": "List of voice profiles",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "profile_123",
                                "name": "John Doe Voice",
                                "language": "en",
                                "quality_score": 4.5,
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "page_size": 50,
                    }
                }
            },
        }
    },
)
@cache_response(ttl=60)  # Cache for 60 seconds
def list_profiles(request: Request) -> dict:
    """
    List all voice profiles with pagination.

    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 50, max: 1000)
    """
    try:
        # Get pagination parameters
        pagination = get_pagination_params(request, default_page_size=50)

        # Get all profiles
        all_profiles = list(_profiles.values())

        # Paginate
        result = pagination.paginate(all_profiles)

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list profiles: {e}", exc_info=True)
        from ..exceptions import VoiceStudioException
        from fastapi import status
        raise VoiceStudioException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list profiles: {str(e)}",
            error_code="INTERNAL_SERVER_ERROR",
            recovery_suggestion="Please try again later. If the issue persists, contact support."
        ) from e


@router.get("/{profile_id}", response_model=VoiceProfile)
@cache_response(ttl=300)  # Cache for 5 minutes
def get_profile(profile_id: str) -> VoiceProfile:
    """Get a specific voice profile."""
    try:
        if profile_id not in _profiles:
            raise ProfileNotFoundException(profile_id)
        return _profiles[profile_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get profile {profile_id}: {e}", exc_info=True)
        from ..exceptions import VoiceStudioException
        from fastapi import status
        raise VoiceStudioException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}",
            error_code="INTERNAL_SERVER_ERROR",
            recovery_suggestion="Please try again later. If the issue persists, contact support.",
            context={"profile_id": profile_id}
        ) from e


@router.post("", response_model=VoiceProfile)
def create_profile(req: ProfileCreateRequest) -> VoiceProfile:
    """Create a new voice profile."""
    try:
        # Validate input
        if not req.name or not req.name.strip():
            from ..exceptions import InvalidInputException
            raise InvalidInputException("Profile name is required and cannot be empty", field="name", value=req.name)

        if not req.language or not req.language.strip():
            from ..exceptions import InvalidInputException
            raise InvalidInputException("Language is required and cannot be empty", field="language", value=req.language)

        import uuid

        profile_id = str(uuid.uuid4())

        profile = VoiceProfile(
            id=profile_id,
            name=req.name.strip(),
            language=req.language.strip(),
            emotion=req.emotion.strip() if req.emotion else None,
            tags=[tag.strip() for tag in req.tags] if req.tags else [],
            quality_score=0.0,
        )

        _profiles[profile_id] = profile
        _profile_timestamps[profile_id] = time.time()

        # Clean up old profiles if needed
        if len(_profiles) > _MAX_PROFILES:
            _cleanup_old_profiles()

        logger.info(f"Created profile: {profile_id} - {profile.name}")
        return profile
    except HTTPException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create profile: {e}", exc_info=True)
        from ..exceptions import VoiceStudioException
        from fastapi import status
        raise VoiceStudioException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}",
            error_code="INTERNAL_SERVER_ERROR",
            recovery_suggestion="Please try again later. If the issue persists, contact support."
        ) from e


@router.put("/{profile_id}", response_model=VoiceProfile)
def update_profile(profile_id: str, req: ProfileUpdateRequest) -> VoiceProfile:
    """Update an existing voice profile."""
    try:
        if profile_id not in _profiles:
            raise ProfileNotFoundException(profile_id)

        # Validate input
        if req.name is not None and (not req.name or not req.name.strip()):
            from ..exceptions import InvalidInputException
            raise InvalidInputException("Profile name cannot be empty", field="name", value=req.name)

        if req.language is not None and (not req.language or not req.language.strip()):
            from ..exceptions import InvalidInputException
            raise InvalidInputException("Language cannot be empty", field="language", value=req.language)

        profile = _profiles[profile_id]

        if req.name is not None:
            profile.name = req.name.strip()
        if req.language is not None:
            profile.language = req.language.strip()
        if req.emotion is not None:
            profile.emotion = req.emotion.strip() if req.emotion else None
        if req.tags is not None:
            profile.tags = [tag.strip() for tag in req.tags] if req.tags else []

        _profiles[profile_id] = profile
        logger.info(f"Updated profile: {profile_id} - {profile.name}")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update profile {profile_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to update profile: {str(e)}"
        ) from e


@router.delete("/{profile_id}", response_model=ApiOk)
def delete_profile(profile_id: str) -> ApiOk:
    """Delete a voice profile."""
    try:
        if profile_id not in _profiles:
            raise ProfileNotFoundException(profile_id)

        del _profiles[profile_id]
        if profile_id in _profile_timestamps:
            del _profile_timestamps[profile_id]
        logger.info(f"Deleted profile: {profile_id}")
        return ApiOk()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete profile {profile_id}: {e}", exc_info=True)
        from ..exceptions import VoiceStudioException
        from fastapi import status
        raise VoiceStudioException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}",
            error_code="INTERNAL_SERVER_ERROR",
            recovery_suggestion="Please try again later. If the issue persists, contact support.",
            context={"profile_id": profile_id}
        ) from e


@router.post(
    "/{profile_id}/preprocess-reference",
    response_model=ReferenceAudioPreprocessResponse,
)
async def preprocess_reference_audio(
    profile_id: str, req: ReferenceAudioPreprocessRequest
) -> ReferenceAudioPreprocessResponse:
    """
    Advanced reference audio pre-processing and optimization (IDEA 62).

    Analyzes reference audio for quality issues, enhances it automatically,
    and selects optimal segments for voice cloning.
    """
    import os
    import tempfile
    import uuid

    import numpy as np

    from ..models_additional import (
        ReferenceAudioAnalysis,
        ReferenceAudioPreprocessRequest,
        ReferenceAudioPreprocessResponse,
    )

    try:
        # Get profile
        if profile_id not in _profiles:
            raise ProfileNotFoundException(profile_id)

        profile = _profiles[profile_id]

        # Get reference audio path
        reference_audio_path = req.reference_audio_path
        if not reference_audio_path:
            if (
                profile.reference_audio_url
                and not profile.reference_audio_url.startswith("http")
            ):
                reference_audio_path = profile.reference_audio_url
            else:
                profile_dir = os.path.join(
                    os.path.expanduser("~"), ".voicestudio", "profiles", profile_id
                )
                for path in [
                    os.path.join(profile_dir, "reference.wav"),
                    os.path.join(profile_dir, "reference_audio.wav"),
                ]:
                    if os.path.exists(path):
                        reference_audio_path = path
                        break

        if not reference_audio_path or not os.path.exists(reference_audio_path):
            from ..exceptions import FileNotFoundException
            raise FileNotFoundException(f"Reference audio for profile {profile_id}")

        # Try to load audio analysis libraries
        try:
            import librosa
            import soundfile as sf

            HAS_AUDIO_LIBS = True
        except ImportError:
            HAS_AUDIO_LIBS = False
            logger.warning(
                "librosa/soundfile not available for reference audio pre-processing"
            )

        if not HAS_AUDIO_LIBS:
            from ..exceptions import VoiceStudioException
            from fastapi import status
            raise VoiceStudioException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audio analysis libraries not available. Install librosa and soundfile.",
                error_code="SERVICE_UNAVAILABLE",
                recovery_suggestion="Please install librosa and soundfile libraries to enable reference audio pre-processing.",
                context={"profile_id": profile_id}
            )

        # Load and analyze original audio
        audio, sample_rate = sf.read(reference_audio_path)
        duration = len(audio) / sample_rate

        # Convert to mono if stereo
        if len(audio.shape) > 1:
            channels = audio.shape[1]
            audio_mono = np.mean(audio, axis=1)
        else:
            channels = 1
            audio_mono = audio

        # Analyze for quality issues
        has_noise = False
        has_clipping = False
        has_distortion = False
        recommendations = []
        quality_score = 10.0  # Start with perfect score

        # Check for clipping
        max_amplitude = np.max(np.abs(audio_mono))
        if max_amplitude >= 0.99:
            has_clipping = True
            quality_score -= 2.0
            recommendations.append("Audio has clipping - reduce input gain")

        # Check for noise (high frequency content when speech should be quiet)
        try:
            # Calculate spectral features
            spectral_centroid = np.mean(
                librosa.feature.spectral_centroid(y=audio_mono, sr=sample_rate)
            )
            spectral_rolloff = np.mean(
                librosa.feature.spectral_rolloff(y=audio_mono, sr=sample_rate)
            )

            # High rolloff with low centroid suggests noise
            if spectral_rolloff > 8000 and spectral_centroid < 1000:
                has_noise = True
                quality_score -= 1.5
                recommendations.append("Background noise detected - apply denoising")
        except:
            pass

        # Check for distortion (unusual spectral characteristics)
        try:
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(audio_mono))
            if zero_crossing_rate > 0.2:  # Unusually high ZCR suggests distortion
                has_distortion = True
                quality_score -= 1.0
                recommendations.append(
                    "Possible distortion detected - check audio source"
                )
        except:
            pass

        # Check sample rate (should be >= 16kHz for good quality)
        if sample_rate < 16000:
            quality_score -= 1.0
            recommendations.append(
                f"Low sample rate ({sample_rate}Hz) - recommend >= 16kHz"
            )

        # Check duration (should be >= 3 seconds for good cloning)
        if duration < 3.0:
            recommendations.append(
                f"Short duration ({duration:.1f}s) - recommend >= 3 seconds for better cloning"
            )
        elif duration > 30.0:
            recommendations.append(
                f"Long duration ({duration:.1f}s) - consider selecting optimal segments"
            )

        quality_score = max(1.0, min(10.0, quality_score))  # Clamp to 1-10

        original_analysis = ReferenceAudioAnalysis(
            quality_score=quality_score,
            has_noise=has_noise,
            has_clipping=has_clipping,
            has_distortion=has_distortion,
            sample_rate=sample_rate,
            duration=duration,
            channels=channels,
            recommendations=recommendations,
            optimal_segments=None,
        )

        # Process audio if auto_enhance is enabled
        processed_audio = audio_mono.copy()
        improvements_applied = []
        quality_improvement = 0.0

        if req.auto_enhance:
            try:
                # Import audio enhancement functions
                import sys

                app_path = os.path.join(
                    os.path.dirname(__file__), "..", "..", "..", "app"
                )
                if os.path.exists(app_path) and app_path not in sys.path:
                    sys.path.insert(0, app_path)

                from core.audio.audio_utils import enhance_voice_quality

                # Enhance audio
                processed_audio = enhance_voice_quality(
                    processed_audio,
                    sample_rate,
                    normalize=True,
                    denoise=has_noise,
                    target_lufs=-23.0,
                )

                if has_noise:
                    improvements_applied.append("Denoising applied")
                improvements_applied.append("Normalization applied")

                # Re-analyze processed audio
                processed_max = np.max(np.abs(processed_audio))
                if processed_max < 0.99 and has_clipping:
                    improvements_applied.append("Clipping reduced")
                    quality_improvement += 0.1

                # Estimate quality improvement
                if has_noise:
                    quality_improvement += 0.15
                if has_clipping:
                    quality_improvement += 0.1

                quality_improvement = min(1.0, quality_improvement)

            except Exception as e:
                logger.warning(f"Audio enhancement failed: {e}")

        # Select optimal segments if requested
        optimal_segments = None
        if req.select_optimal_segments:
            try:
                # Simple segment selection based on RMS energy (voice activity)
                segment_duration = max(req.min_segment_duration, 1.0)
                hop_length = int(sample_rate * 0.5)  # 0.5s hop
                frame_length = int(sample_rate * segment_duration)

                segments = []
                for i in range(0, len(processed_audio) - frame_length, hop_length):
                    segment = processed_audio[i : i + frame_length]
                    rms = np.sqrt(np.mean(segment**2))

                    # Prefer segments with good RMS (voice activity) and no clipping
                    if rms > 0.01 and np.max(np.abs(segment)) < 0.95:
                        segments.append(
                            {
                                "start_time": i / sample_rate,
                                "end_time": (i + frame_length) / sample_rate,
                                "duration": segment_duration,
                                "rms_energy": float(rms),
                                "quality_score": float(min(10.0, rms * 100)),
                            }
                        )

                # Sort by quality and select best
                segments.sort(key=lambda x: x["quality_score"], reverse=True)
                optimal_segments = segments[: req.max_segments]

                if optimal_segments:
                    original_analysis.optimal_segments = optimal_segments
                    improvements_applied.append(
                        f"Selected {len(optimal_segments)} optimal segments"
                    )

            except Exception as e:
                logger.warning(f"Segment selection failed: {e}")

        # Save processed audio if enhanced
        processed_audio_id = None
        processed_audio_url = None
        processed_analysis = None

        if req.auto_enhance and improvements_applied:
            processed_audio_id = f"processed_{profile_id}_{uuid.uuid4().hex[:8]}"
            processed_path = tempfile.mktemp(suffix=".wav")

            # Ensure audio is in correct format
            if processed_audio.dtype != np.float32:
                processed_audio = processed_audio.astype(np.float32)
            processed_audio = np.clip(processed_audio, -1.0, 1.0)

            # Save processed audio
            sf.write(processed_path, processed_audio, sample_rate)

            # Register audio file
            from .voice import _register_audio_file

            _register_audio_file(processed_audio_id, processed_path)

            processed_audio_url = f"/api/voice/audio/{processed_audio_id}"

            # Create processed analysis
            processed_quality = min(10.0, quality_score + quality_improvement * 2.0)
            processed_analysis = ReferenceAudioAnalysis(
                quality_score=processed_quality,
                has_noise=False if "Denoising" in improvements_applied else has_noise,
                has_clipping=(
                    False
                    if "Clipping reduced" in improvements_applied
                    else has_clipping
                ),
                has_distortion=has_distortion,
                sample_rate=sample_rate,
                duration=duration,
                channels=1,
                recommendations=[],
                optimal_segments=optimal_segments,
            )

        return ReferenceAudioPreprocessResponse(
            processed_audio_id=processed_audio_id or f"original_{profile_id}",
            processed_audio_url=processed_audio_url
            or f"/api/profiles/{profile_id}/reference",
            original_analysis=original_analysis,
            processed_analysis=processed_analysis,
            improvements_applied=improvements_applied,
            quality_improvement=quality_improvement,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reference audio pre-processing error: {e}", exc_info=True)
        from ..exceptions import VoiceStudioException
        from fastapi import status
        raise VoiceStudioException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reference audio pre-processing failed: {str(e)}",
            error_code="AUDIO_PROCESSING_ERROR",
            recovery_suggestion="Please check the audio file format and try again.",
            context={"profile_id": profile_id}
        ) from e
