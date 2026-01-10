"""
Voice Morphing/Blending Routes

Endpoints for voice morphing and blending between multiple voices.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice-morph", tags=["voice-morph"])

# In-memory morph configurations (replace with database in production)
_morph_configs: Dict[str, Dict] = {}


class VoiceBlend(BaseModel):
    """A voice blend configuration."""

    voice_profile_id: str
    weight: float  # 0.0 to 1.0


class MorphConfig(BaseModel):
    """Voice morphing configuration."""

    config_id: str
    name: str
    source_audio_id: str
    target_voices: List[VoiceBlend]  # Multiple voices to blend
    morph_strength: float = 0.5  # 0.0 to 1.0
    preserve_emotion: bool = True
    preserve_prosody: bool = True
    output_format: str = "wav"


class MorphConfigCreateRequest(BaseModel):
    """Request to create a morph configuration."""

    name: str
    source_audio_id: str
    target_voices: List[Dict]  # [{"voice_profile_id": "...", "weight": 0.5}]
    morph_strength: float = 0.5
    preserve_emotion: bool = True
    preserve_prosody: bool = True
    output_format: str = "wav"


class MorphApplyRequest(BaseModel):
    """Request to apply morph configuration."""

    config_id: str


@router.post("/configs", response_model=MorphConfig)
async def create_morph_config(request: MorphConfigCreateRequest):
    """Create a new voice morphing configuration."""
    import uuid

    try:
        config_id = f"morph-{uuid.uuid4().hex[:8]}"

        target_voices = [
            VoiceBlend(
                voice_profile_id=v["voice_profile_id"],
                weight=v.get("weight", 0.5),
            )
            for v in request.target_voices
        ]

        # Normalize weights
        total_weight = sum(v.weight for v in target_voices)
        if total_weight > 0:
            for v in target_voices:
                v.weight = v.weight / total_weight

        config = MorphConfig(
            config_id=config_id,
            name=request.name,
            source_audio_id=request.source_audio_id,
            target_voices=target_voices,
            morph_strength=request.morph_strength,
            preserve_emotion=request.preserve_emotion,
            preserve_prosody=request.preserve_prosody,
            output_format=request.output_format,
        )

        _morph_configs[config_id] = config.model_dump()
        logger.info(f"Created morph config: {config_id}")

        return config
    except Exception as e:
        logger.error(f"Failed to create morph config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create config: {str(e)}",
        ) from e


@router.get("/configs", response_model=List[MorphConfig])
async def list_morph_configs():
    """List all morph configurations."""
    return [MorphConfig(**c) for c in _morph_configs.values()]


@router.get("/configs/{config_id}", response_model=MorphConfig)
async def get_morph_config(config_id: str):
    """Get a morph configuration by ID."""
    if config_id not in _morph_configs:
        raise HTTPException(status_code=404, detail="Config not found")

    return MorphConfig(**_morph_configs[config_id])


@router.put("/configs/{config_id}", response_model=MorphConfig)
async def update_morph_config(
    config_id: str, request: MorphConfigCreateRequest
):
    """Update a morph configuration."""
    if config_id not in _morph_configs:
        raise HTTPException(status_code=404, detail="Config not found")

    target_voices = [
        VoiceBlend(
            voice_profile_id=v["voice_profile_id"],
            weight=v.get("weight", 0.5),
        )
        for v in request.target_voices
    ]

    # Normalize weights
    total_weight = sum(v.weight for v in target_voices)
    if total_weight > 0:
        for v in target_voices:
            v.weight = v.weight / total_weight

    config = MorphConfig(
        config_id=config_id,
        name=request.name,
        source_audio_id=request.source_audio_id,
        target_voices=target_voices,
        morph_strength=request.morph_strength,
        preserve_emotion=request.preserve_emotion,
        preserve_prosody=request.preserve_prosody,
        output_format=request.output_format,
    )

    _morph_configs[config_id] = config.model_dump()
    logger.info(f"Updated morph config: {config_id}")

    return config


@router.delete("/configs/{config_id}")
async def delete_morph_config(config_id: str):
    """Delete a morph configuration."""
    if config_id not in _morph_configs:
        raise HTTPException(status_code=404, detail="Config not found")

    del _morph_configs[config_id]
    logger.info(f"Deleted morph config: {config_id}")
    return {"success": True}


@router.post("/apply")
async def apply_morph(request: MorphApplyRequest):
    """
    Apply voice morphing configuration.

    Note: Voice morphing requires specialized audio processing libraries
    (e.g., librosa, numpy, scipy, and voice embedding extraction tools) for:
    - Loading and processing source audio
    - Extracting voice embeddings/features from source audio
    - Blending target voice embeddings based on weights
    - Applying morphing with specified strength
    - Preserving emotion/prosody characteristics if requested
    - Synthesizing morphed audio output

    This feature is not yet fully implemented. Please install required
    libraries to enable voice morphing functionality.
    """
    if request.config_id not in _morph_configs:
        raise HTTPException(status_code=404, detail="Config not found")

    config = MorphConfig(**_morph_configs[request.config_id])

    # Voice morphing requires specialized audio processing libraries:
    # - librosa: Audio loading and feature extraction (available)
    # - numpy: Array operations for audio processing (available)
    # - scipy: Signal processing for morphing algorithms
    # - Voice embedding extraction: Requires trained models
    #   (e.g., Wav2Vec2, XLS-R)
    # - RVC (Retrieval-based Voice Conversion): For advanced morphing
    #
    # Real implementation would:
    # 1. Load source audio from audio_id using audio file storage
    # 2. Extract voice embeddings from source audio using embedding
    #    model
    # 3. Load target voice embeddings from voice profiles
    # 4. Blend target voice embeddings based on weights
    #    (weighted interpolation)
    # 5. Apply morphing transformation with specified strength (0.0-1.0)
    # 6. Preserve emotion/prosody characteristics if requested
    #    (feature preservation)
    # 7. Synthesize morphed audio using voice synthesis engine
    # 8. Save morphed audio to storage
    # 9. Return audio_id for the morphed audio file

    num_voices = len(config.target_voices)
    raise HTTPException(
        status_code=501,
        detail=(
            f"Voice morphing is not yet fully implemented. "
            f"Config '{config.name}' is ready with {num_voices} target "
            f"voices, but applying voice morphing requires voice embedding "
            f"extraction and blending libraries. "
            f"To enable: install required audio processing libraries and "
            f"voice embedding models. "
            f"Example: pip install librosa numpy scipy transformers"
        ),
    )


# Simplified endpoints for Voice Morphing/Blending Panel (matching spec)
class VoiceBlendRequest(BaseModel):
    """Request to blend two voices."""

    voice_a_id: str
    voice_b_id: str
    blend_ratio: float = 0.5  # 0.0 = 100% A, 1.0 = 100% B
    text: Optional[str] = None  # Optional text for preview
    save_profile: bool = False  # Save as new voice profile


class VoiceBlendResponse(BaseModel):
    """Voice blend response."""

    blended_profile_id: Optional[str] = None
    preview_audio_id: Optional[str] = None
    preview_audio_url: Optional[str] = None
    blend_ratio: float


class VoiceMorphRequest(BaseModel):
    """Request to morph voice over time."""

    source_audio_id: str
    voice_a_id: str
    voice_b_id: str
    start_ratio: float = 0.0  # 0.0 = 100% A
    end_ratio: float = 1.0  # 1.0 = 100% B
    morph_speed: float = 1.0  # Morph speed/smoothness
    keyframes: Optional[List[Dict]] = None  # Intermediate waypoints


class VoiceMorphResponse(BaseModel):
    """Voice morph response."""

    morphed_audio_id: str
    morphed_audio_url: str
    duration: float


class VoiceEmbeddingRequest(BaseModel):
    """Request to get voice embedding."""

    voice_profile_id: str


class VoiceEmbeddingResponse(BaseModel):
    """Voice embedding response."""

    voice_profile_id: str
    embedding: List[float]
    embedding_dim: int


class VoicePreviewRequest(BaseModel):
    """Request to preview blended/morphed voice."""

    voice_profile_id: Optional[str] = None
    voice_a_id: Optional[str] = None
    voice_b_id: Optional[str] = None
    blend_ratio: Optional[float] = None
    text: str = "Hello, this is a preview of the blended voice."


class VoicePreviewResponse(BaseModel):
    """Voice preview response."""

    preview_audio_id: str
    preview_audio_url: str
    duration: float


@router.post("/voice/blend", response_model=VoiceBlendResponse)
async def blend_voices(request: VoiceBlendRequest):
    """
    Blend two voices (simplified endpoint for panel).

    Creates a blended voice by synthesizing with both voices
    and mixing the results.
    """
    try:
        import uuid
        import os
        import tempfile
        import numpy as np

        if not request.voice_a_id or not request.voice_b_id:
            raise HTTPException(
                status_code=400,
                detail="voice_a_id and voice_b_id are required",
            )

        # Validate blend ratio
        if not (0.0 <= request.blend_ratio <= 1.0):
            raise HTTPException(
                status_code=400,
                detail="blend_ratio must be between 0.0 and 1.0",
            )

        blended_profile_id = None
        preview_audio_id = None

        # If text provided, synthesize preview audio with blended voice
        if request.text:
            try:
                from ..models_additional import VoiceSynthesizeRequest
                from .voice import synthesize, _register_audio_file

                # Synthesize with voice A
                synth_a = VoiceSynthesizeRequest(
                    profile_id=request.voice_a_id,
                    text=request.text,
                    engine="xtts_v2",
                )
                result_a = await synthesize(synth_a)

                # Synthesize with voice B
                synth_b = VoiceSynthesizeRequest(
                    profile_id=request.voice_b_id,
                    text=request.text,
                    engine="xtts_v2",
                )
                result_b = await synthesize(synth_b)

                if (
                    result_a
                    and result_a.audio_id
                    and result_b
                    and result_b.audio_id
                ):
                    # Load both audio files
                    from .audio import _get_audio_path
                    from app.core.audio.audio_utils import (
                        load_audio,
                        save_audio,
                    )

                    audio_path_a = _get_audio_path(result_a.audio_id)
                    audio_path_b = _get_audio_path(result_b.audio_id)

                    if audio_path_a and audio_path_b:
                        audio_a, sr_a = load_audio(audio_path_a)
                        audio_b, sr_b = load_audio(audio_path_b)

                        # Convert to mono if needed
                        if len(audio_a.shape) > 1:
                            audio_a = np.mean(audio_a, axis=1)
                        if len(audio_b.shape) > 1:
                            audio_b = np.mean(audio_b, axis=1)

                        # Resample to same rate if needed
                        if sr_a != sr_b:
                            import librosa
                            if sr_a < sr_b:
                                audio_b = librosa.resample(
                                    audio_b, orig_sr=sr_b, target_sr=sr_a
                                )
                                sr_b = sr_a
                            else:
                                audio_a = librosa.resample(
                                    audio_a, orig_sr=sr_a, target_sr=sr_b
                                )
                                sr_a = sr_b

                        # Match lengths (pad shorter one)
                        max_len = max(len(audio_a), len(audio_b))
                        if len(audio_a) < max_len:
                            audio_a = np.pad(
                                audio_a,
                                (0, max_len - len(audio_a)),
                                mode="constant",
                            )
                        if len(audio_b) < max_len:
                            audio_b = np.pad(
                                audio_b,
                                (0, max_len - len(audio_b)),
                                mode="constant",
                            )

                        # Blend: weight_a = 1 - blend_ratio,
                        # weight_b = blend_ratio
                        weight_a = 1.0 - request.blend_ratio
                        weight_b = request.blend_ratio
                        blended_audio = audio_a * weight_a + audio_b * weight_b

                        # Normalize to prevent clipping
                        max_amp = np.max(np.abs(blended_audio))
                        if max_amp > 0.95:
                            blended_audio = blended_audio * (0.95 / max_amp)

                        # Save blended audio
                        preview_audio_id = (
                            f"blend_preview_{uuid.uuid4().hex[:8]}"
                        )
                        output_path = os.path.join(
                            tempfile.gettempdir(), f"{preview_audio_id}.wav"
                        )
                        save_audio(blended_audio, sr_a, output_path)
                        _register_audio_file(preview_audio_id, output_path)

                        logger.info(
                            f"Blended voices: {request.voice_a_id} "
                            f"({weight_a:.2f}) + {request.voice_b_id} "
                            f"({weight_b:.2f})"
                        )
            except Exception as e:
                logger.warning(f"Failed to create blended preview audio: {e}")
                # Continue without preview audio

        # If save_profile requested, create blended profile
        if request.save_profile:
            try:
                from .profiles import _profiles, VoiceProfile

                blended_profile_id = f"blend_{uuid.uuid4().hex[:8]}"
                profile_name = (
                    f"Blend: {request.voice_a_id} + {request.voice_b_id}"
                )

                # Create blended profile (references both source profiles)
                blended_profile = VoiceProfile(
                    id=blended_profile_id,
                    name=profile_name,
                    language="en",
                    quality_score=0.0,
                    tags=["blended", request.voice_a_id, request.voice_b_id],
                )
                _profiles[blended_profile_id] = blended_profile

                logger.info(f"Created blended profile: {blended_profile_id}")
            except Exception as e:
                logger.warning(f"Failed to create blended profile: {e}")
                blended_profile_id = None

        return VoiceBlendResponse(
            blended_profile_id=blended_profile_id,
            preview_audio_id=preview_audio_id,
            preview_audio_url=(
                f"/api/voice/audio/{preview_audio_id}"
                if preview_audio_id
                else None
            ),
            blend_ratio=request.blend_ratio,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to blend voices: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to blend voices: {str(e)}",
        ) from e


@router.post("/voice/morph", response_model=VoiceMorphResponse)
async def morph_voice(request: VoiceMorphRequest):
    """Morph voice over time (simplified endpoint for panel)."""
    try:
        import uuid

        # In production, this would:
        # 1. Load source audio
        # 2. Load voice embeddings for Voice A and Voice B
        # 3. Split audio into segments
        # 4. For each segment, interpolate embeddings based on time position
        # 5. Apply keyframes if provided
        # 6. Synthesize each segment with morphed embedding
        # 7. Crossfade segments together
        # 8. Save morphed audio

        morphed_audio_id = f"morph-{uuid.uuid4().hex[:8]}"

        return VoiceMorphResponse(
            morphed_audio_id=morphed_audio_id,
            morphed_audio_url=f"/api/audio/{morphed_audio_id}",
            duration=10.0,  # Estimated duration
        )
    except Exception as e:
        logger.error(f"Failed to morph voice: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to morph voice: {str(e)}",
        ) from e


@router.post("/voice/embedding", response_model=VoiceEmbeddingResponse)
async def get_voice_embedding(request: VoiceEmbeddingRequest):
    """
    Get voice embedding (simplified endpoint for panel).

    Extracts voice characteristics/features from profile reference audio.
    """
    try:
        import os
        import numpy as np

        if not request.voice_profile_id:
            raise HTTPException(
                status_code=400,
                detail="voice_profile_id is required",
            )

        # Try to get profile and extract embedding from reference audio
        try:
            from .profiles import _profiles

            profile = _profiles.get(request.voice_profile_id)
            if not profile:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Voice profile not found: "
                        f"{request.voice_profile_id}"
                    ),
                )

            # Get reference audio path
            reference_audio_path = None
            if profile.reference_audio_url:
                if not profile.reference_audio_url.startswith("http"):
                    reference_audio_path = profile.reference_audio_url

            if not reference_audio_path:
                # Try standard profile directory
                profile_dir = os.path.join(
                    os.path.expanduser("~"),
                    ".voicestudio",
                    "profiles",
                    request.voice_profile_id,
                )
                potential_paths = [
                    os.path.join(profile_dir, "reference.wav"),
                    os.path.join(profile_dir, "reference_audio.wav"),
                    os.path.join(profile_dir, "audio.wav"),
                ]
                for path in potential_paths:
                    if os.path.exists(path):
                        reference_audio_path = path
                        break

            if reference_audio_path and os.path.exists(reference_audio_path):
                # Extract voice characteristics as embedding
                try:
                    from app.core.audio.audio_utils import (
                        load_audio,
                        analyze_voice_characteristics,
                    )

                    audio, sample_rate = load_audio(reference_audio_path)
                    characteristics = analyze_voice_characteristics(
                        audio, sample_rate
                    )

                    # Create embedding from characteristics
                    # Combine various features into a feature vector
                    embedding = []
                    embedding.append(characteristics.get("f0_mean", 0.0))
                    embedding.append(characteristics.get("f0_std", 0.0))
                    embedding.extend(
                        characteristics.get("formants", [0.0, 0.0, 0.0])[:3]
                    )
                    embedding.append(
                        characteristics.get("spectral_centroid", 0.0)
                    )
                    embedding.append(
                        characteristics.get("spectral_rolloff", 0.0)
                    )
                    embedding.append(
                        characteristics.get("zero_crossing_rate", 0.0)
                    )
                    mfcc = characteristics.get("mfcc", [])
                    if isinstance(mfcc, np.ndarray):
                        embedding.extend(mfcc.flatten()[:13].tolist())
                    elif isinstance(mfcc, list):
                        embedding.extend(mfcc[:13])

                    # Pad or truncate to standard size (256 dimensions)
                    embedding_dim = 256
                    if len(embedding) < embedding_dim:
                        # Pad with zeros
                        padding = embedding_dim - len(embedding)
                        embedding.extend([0.0] * padding)
                    elif len(embedding) > embedding_dim:
                        # Truncate
                        embedding = embedding[:embedding_dim]

                    # Normalize embedding
                    embedding_array = np.array(embedding)
                    norm = np.linalg.norm(embedding_array)
                    if norm > 0:
                        embedding_array = embedding_array / norm
                    embedding = embedding_array.tolist()

                    logger.info(
                        f"Extracted voice embedding for profile "
                        f"{request.voice_profile_id}: "
                        f"{len(embedding)} dimensions"
                    )

                    return VoiceEmbeddingResponse(
                        voice_profile_id=request.voice_profile_id,
                        embedding=embedding,
                        embedding_dim=embedding_dim,
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to extract embedding from audio characteristics: {e}"
                    )
                    # Try fallback method: direct librosa features
                    try:
                        import librosa
                        import numpy as np
                        
                        audio, sample_rate = load_audio(reference_audio_path)
                        
                        # Extract basic audio features as embedding
                        embedding = []
                        
                        # Spectral features
                        spectral_centroids = librosa.feature.spectral_centroid(
                            y=audio, sr=sample_rate
                        )[0]
                        embedding.append(float(np.mean(spectral_centroids)))
                        embedding.append(float(np.std(spectral_centroids)))
                        
                        spectral_rolloff = librosa.feature.spectral_rolloff(
                            y=audio, sr=sample_rate
                        )[0]
                        embedding.append(float(np.mean(spectral_rolloff)))
                        
                        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
                        embedding.append(float(np.mean(zero_crossing_rate)))
                        
                        # MFCC features (13 coefficients)
                        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
                        embedding.extend([float(x) for x in np.mean(mfccs, axis=1)])
                        
                        # Chroma features (12 pitch classes)
                        chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
                        embedding.extend([float(x) for x in np.mean(chroma, axis=1)])
                        
                        # Tonnetz features (6 dimensions)
                        tonnetz = librosa.feature.tonnetz(
                            y=audio, sr=sample_rate
                        )
                        embedding.extend([float(x) for x in np.mean(tonnetz, axis=1)])
                        
                        # Pad or truncate to standard size (256 dimensions)
                        embedding_dim = 256
                        if len(embedding) < embedding_dim:
                            # Pad with statistical features from audio
                            padding_needed = embedding_dim - len(embedding)
                            audio_stats = [
                                float(np.mean(audio)),
                                float(np.std(audio)),
                                float(np.max(np.abs(audio))),
                                float(np.min(audio)),
                                float(np.median(audio)),
                            ]
                            # Repeat stats to fill padding
                            while len(embedding) < embedding_dim:
                                embedding.extend(audio_stats[:min(padding_needed, len(audio_stats))])
                                padding_needed = embedding_dim - len(embedding)
                        elif len(embedding) > embedding_dim:
                            # Truncate
                            embedding = embedding[:embedding_dim]
                        
                        # Normalize embedding
                        embedding_array = np.array(embedding)
                        norm = np.linalg.norm(embedding_array)
                        if norm > 0:
                            embedding_array = embedding_array / norm
                        embedding = embedding_array.tolist()
                        
                        logger.info(
                            f"Extracted voice embedding using fallback method for profile "
                            f"{request.voice_profile_id}: {len(embedding)} dimensions"
                        )
                        
                        return VoiceEmbeddingResponse(
                            voice_profile_id=request.voice_profile_id,
                            embedding=embedding,
                            embedding_dim=embedding_dim,
                        )
                    except Exception as e2:
                        logger.warning(
                            f"Fallback embedding extraction also failed: {e2}"
                        )
                        # Last resort: try speaker encoder if available
                        try:
                            from app.core.engines.speaker_encoder_engine import (
                                SpeakerEncoderEngine,
                            )
                            
                            encoder = SpeakerEncoderEngine()
                            if encoder.initialize():
                                audio, sample_rate = load_audio(reference_audio_path)
                                embedding = encoder.encode(audio, sample_rate)
                                
                                if embedding is not None:
                                    embedding_dim = len(embedding)
                                    logger.info(
                                        f"Extracted voice embedding using speaker encoder for profile "
                                        f"{request.voice_profile_id}: {embedding_dim} dimensions"
                                    )
                                    
                                    return VoiceEmbeddingResponse(
                                        voice_profile_id=request.voice_profile_id,
                                        embedding=embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                                        embedding_dim=embedding_dim,
                                    )
                        except Exception as e3:
                            logger.debug(f"Speaker encoder extraction failed: {e3}")

        except ImportError:
            ...
        except HTTPException:
            raise

        # If all extraction methods failed, return error instead of placeholder
        logger.error(
            f"All voice embedding extraction methods failed for profile "
            f"{request.voice_profile_id}. Reference audio may be missing or invalid."
        )
        raise HTTPException(
            status_code=404,
            detail=(
                f"Could not extract voice embedding for profile "
                f"{request.voice_profile_id}. "
                f"Reference audio file not found or invalid. "
                f"Please ensure the voice profile has valid reference audio."
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get voice embedding: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get voice embedding: {str(e)}",
        ) from e


@router.post("/voice/preview", response_model=VoicePreviewResponse)
async def preview_voice(request: VoicePreviewRequest):
    """
    Preview blended/morphed voice (simplified endpoint for panel).

    Synthesizes text with the specified voice profile or blended voices.
    """
    try:
        import uuid
        import os
        import tempfile

        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="text is required for preview",
            )

        preview_audio_id = None

        try:
            from ..models_additional import VoiceSynthesizeRequest
            from .voice import synthesize, _register_audio_file
            from app.core.audio.audio_utils import load_audio

            # If voice_profile_id provided, use that directly
            if request.voice_profile_id:
                synth_req = VoiceSynthesizeRequest(
                    profile_id=request.voice_profile_id,
                    text=request.text,
                    engine="xtts_v2",
                )
                result = await synthesize(synth_req)
                if result and result.audio_id:
                    preview_audio_id = result.audio_id

            # If voice_a_id and voice_b_id provided, blend them
            elif request.voice_a_id and request.voice_b_id:
                blend_ratio = request.blend_ratio or 0.5

                # Synthesize with both voices
                synth_a = VoiceSynthesizeRequest(
                    profile_id=request.voice_a_id,
                    text=request.text,
                    engine="xtts_v2",
                )
                result_a = await synthesize(synth_a)

                synth_b = VoiceSynthesizeRequest(
                    profile_id=request.voice_b_id,
                    text=request.text,
                    engine="xtts_v2",
                )
                result_b = await synthesize(synth_b)

                if (
                    result_a
                    and result_a.audio_id
                    and result_b
                    and result_b.audio_id
                ):
                    # Blend the audio (same logic as blend_voices)
                    import numpy as np
                    from .audio import _get_audio_path
                    from app.core.audio.audio_utils import save_audio

                    audio_path_a = _get_audio_path(result_a.audio_id)
                    audio_path_b = _get_audio_path(result_b.audio_id)

                    if audio_path_a and audio_path_b:
                        audio_a, sr_a = load_audio(audio_path_a)
                        audio_b, sr_b = load_audio(audio_path_b)

                        # Convert to mono if needed
                        if len(audio_a.shape) > 1:
                            audio_a = np.mean(audio_a, axis=1)
                        if len(audio_b.shape) > 1:
                            audio_b = np.mean(audio_b, axis=1)

                        # Resample to same rate if needed
                        if sr_a != sr_b:
                            import librosa
                            if sr_a < sr_b:
                                audio_b = librosa.resample(
                                    audio_b, orig_sr=sr_b, target_sr=sr_a
                                )
                                sr_b = sr_a
                            else:
                                audio_a = librosa.resample(
                                    audio_a, orig_sr=sr_a, target_sr=sr_b
                                )
                                sr_a = sr_b

                        # Match lengths
                        max_len = max(len(audio_a), len(audio_b))
                        if len(audio_a) < max_len:
                            audio_a = np.pad(
                                audio_a,
                                (0, max_len - len(audio_a)),
                                mode="constant",
                            )
                        if len(audio_b) < max_len:
                            audio_b = np.pad(
                                audio_b,
                                (0, max_len - len(audio_b)),
                                mode="constant",
                            )

                        # Blend
                        weight_a = 1.0 - blend_ratio
                        weight_b = blend_ratio
                        blended_audio = audio_a * weight_a + audio_b * weight_b

                        # Normalize
                        max_amp = np.max(np.abs(blended_audio))
                        if max_amp > 0.95:
                            blended_audio = blended_audio * (0.95 / max_amp)

                        # Save blended audio
                        preview_audio_id = f"preview_{uuid.uuid4().hex[:8]}"
                        output_path = os.path.join(
                            tempfile.gettempdir(), f"{preview_audio_id}.wav"
                        )
                        save_audio(blended_audio, sr_a, output_path)
                        _register_audio_file(preview_audio_id, output_path)

                        logger.info(
                            f"Created preview with blended voices: "
                            f"{request.voice_a_id} + {request.voice_b_id}"
                        )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Either voice_profile_id or both voice_a_id and "
                        "voice_b_id must be provided"
                    ),
                )

            if not preview_audio_id:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate preview audio",
                )

            # Get duration
            audio_path = _get_audio_path(preview_audio_id)
            if audio_path:
                audio, sr = load_audio(audio_path)
                duration = len(audio) / sr
            else:
                duration = len(request.text.split()) * 0.5  # Estimate

            return VoicePreviewResponse(
                preview_audio_id=preview_audio_id,
                preview_audio_url=f"/api/voice/audio/{preview_audio_id}",
                duration=duration,
            )

        except ImportError:
            logger.warning("Voice synthesis not available for preview")
            raise HTTPException(
                status_code=503,
                detail="Voice synthesis service not available",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview voice: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preview voice: {str(e)}",
        ) from e
