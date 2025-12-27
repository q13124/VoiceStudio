"""
VoiceStudio Engine Modules

Engines for voice cloning, synthesis, and transcription.
"""

from .aeneas_engine import AeneasEngine, create_aeneas_engine
from .automatic1111_engine import Automatic1111Engine, create_automatic1111_engine
from .bark_engine import BarkEngine, create_bark_engine
from .chatterbox_engine import ChatterboxEngine, create_chatterbox_engine
from .comfyui_engine import ComfyUIEngine, create_comfyui_engine
from .config import EngineConfig, get_engine_config
from .deepfacelab_engine import DeepFaceLabEngine, create_deepfacelab_engine
from .deforum_engine import DeforumEngine, create_deforum_engine
from .espeak_ng_engine import ESpeakNGEngine, create_espeak_ng_engine
from .f5_tts_engine import F5TTSEngine, create_f5_tts_engine
from .fastsd_cpu_engine import FastSDCPUEngine, create_fastsd_cpu_engine
from .festival_flite_engine import FestivalFliteEngine, create_festival_flite_engine
from .ffmpeg_ai_engine import FFmpegAIEngine, create_ffmpeg_ai_engine
from .fomm_engine import FOMMEngine, create_fomm_engine
from .fooocus_engine import FooocusEngine, create_fooocus_engine
from .gpt_sovits_engine import GPTSovitsEngine, create_gpt_sovits_engine
from .higgs_audio_engine import HiggsAudioEngine, create_higgs_audio_engine
from .invokeai_engine import InvokeAIEngine, create_invokeai_engine
from .localai_engine import LocalAIEngine, create_localai_engine
from .lyrebird_engine import LyrebirdEngine, create_lyrebird_engine
from .manifest_loader import (
    find_engine_manifests,
    get_engine_config_schema,
    get_engine_entry_point,
    load_engine_manifest,
    validate_engine_requirements,
)
from .marytts_engine import MaryTTSEngine, create_marytts_engine
from .mockingbird_engine import MockingBirdEngine, create_mockingbird_engine
from .moviepy_engine import MoviePyEngine, create_moviepy_engine
from .openai_tts_engine import OpenAITTSEngine, create_openai_tts_engine
from .openjourney_engine import OpenJourneyEngine, create_openjourney_engine
from .openvoice_engine import OpenVoiceEngine, create_openvoice_engine
from .parakeet_engine import ParakeetEngine, create_parakeet_engine
from .piper_engine import PiperEngine, create_piper_engine
from .protocols import EngineProtocol

# Quality comparison
from .quality_comparison import QualityComparison, compare_audio_samples
from .quality_metrics import (
    calculate_all_metrics,
    calculate_mos_score,
    calculate_naturalness,
    calculate_similarity,
    calculate_snr,
    clear_metrics_cache,
    detect_artifacts,
    get_cache_stats,
)

# Quality optimization
from .quality_optimizer import (
    PROFESSIONAL_THRESHOLDS,
    QUALITY_TIERS,
    QualityOptimizer,
    optimize_synthesis_for_quality,
)

# Quality presets
from .quality_presets import (
    ENGINE_PRESET_MAPPINGS,
    QUALITY_PRESETS,
    get_engine_preset,
    get_preset_description,
    get_preset_target_metrics,
    get_quality_preset,
    get_synthesis_params_from_preset,
    list_quality_presets,
)
from .realesrgan_engine import RealESRGANEngine, create_realesrgan_engine
from .realistic_vision_engine import (
    RealisticVisionEngine,
    create_realistic_vision_engine,
)
from .rhvoice_engine import RHVoiceEngine, create_rhvoice_engine
from .router import EngineRouter, router
from .rvc_engine import RVCEngine, create_rvc_engine
from .sadtalker_engine import SadTalkerEngine, create_sadtalker_engine
from .sd_cpu_engine import SDCPUEngine, create_sd_cpu_engine
from .speaker_encoder_engine import SpeakerEncoderEngine, create_speaker_encoder_engine

# ONNX utilities
try:
    from .onnx_converter import (
        convert_pytorch_to_onnx,
        get_onnx_model_info,
        optimize_onnx_model,
        quantize_onnx_model,
        validate_onnx_model,
    )
    from .onnx_wrapper import ONNXInferenceEngine, create_onnx_inference_engine

    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False
    convert_pytorch_to_onnx = None
    optimize_onnx_model = None
    quantize_onnx_model = None
    validate_onnx_model = None
    get_onnx_model_info = None
    ONNXInferenceEngine = None
    create_onnx_inference_engine = None
from .sdnext_engine import SDNextEngine, create_sdnext_engine
from .sdxl_comfy_engine import SDXLComfyEngine, create_sdxl_comfy_engine
from .sdxl_engine import SDXLEngine, create_sdxl_engine
from .silero_engine import SileroEngine, create_silero_engine
from .svd_engine import SVDEngine, create_svd_engine
from .tortoise_engine import TortoiseEngine, create_tortoise_engine
from .video_creator_engine import VideoCreatorEngine, create_video_creator_engine
from .voice_ai_engine import VoiceAIEngine, create_voice_ai_engine
from .voxcpm_engine import VoxCPMEngine, create_voxcpm_engine
from .whisper_cpp_engine import WhisperCPPEngine, create_whisper_cpp_engine
from .whisper_engine import WhisperEngine, create_whisper_engine
from .whisper_ui_engine import WhisperUIEngine, create_whisper_ui_engine
from .xtts_engine import XTTSEngine, create_xtts_engine

__all__ = [
    "EngineProtocol",
    "XTTSEngine",
    "create_xtts_engine",
    "ChatterboxEngine",
    "create_chatterbox_engine",
    "TortoiseEngine",
    "create_tortoise_engine",
    "WhisperEngine",
    "create_whisper_engine",
    "WhisperCPPEngine",
    "create_whisper_cpp_engine",
    "WhisperUIEngine",
    "create_whisper_ui_engine",
    "GPTSovitsEngine",
    "create_gpt_sovits_engine",
    "MaryTTSEngine",
    "create_marytts_engine",
    "FestivalFliteEngine",
    "create_festival_flite_engine",
    "ESpeakNGEngine",
    "create_espeak_ng_engine",
    "RHVoiceEngine",
    "create_rhvoice_engine",
    "SileroEngine",
    "create_silero_engine",
    "F5TTSEngine",
    "create_f5_tts_engine",
    "AeneasEngine",
    "create_aeneas_engine",
    "BarkEngine",
    "create_bark_engine",
    "ParakeetEngine",
    "create_parakeet_engine",
    "PiperEngine",
    "create_piper_engine",
    "VoxCPMEngine",
    "create_voxcpm_engine",
    "HiggsAudioEngine",
    "create_higgs_audio_engine",
    "OpenVoiceEngine",
    "create_openvoice_engine",
    "RVCEngine",
    "create_rvc_engine",
    "SDXLComfyEngine",
    "create_sdxl_comfy_engine",
    "ComfyUIEngine",
    "create_comfyui_engine",
    "Automatic1111Engine",
    "create_automatic1111_engine",
    "SDNextEngine",
    "create_sdnext_engine",
    "InvokeAIEngine",
    "create_invokeai_engine",
    "FooocusEngine",
    "create_fooocus_engine",
    "LocalAIEngine",
    "create_localai_engine",
    "MockingBirdEngine",
    "create_mockingbird_engine",
    "SDXLEngine",
    "create_sdxl_engine",
    "RealisticVisionEngine",
    "create_realistic_vision_engine",
    "OpenJourneyEngine",
    "create_openjourney_engine",
    "OpenAITTSEngine",
    "create_openai_tts_engine",
    "SDCPUEngine",
    "create_sd_cpu_engine",
    "FastSDCPUEngine",
    "create_fastsd_cpu_engine",
    "RealESRGANEngine",
    "create_realesrgan_engine",
    "SVDEngine",
    "create_svd_engine",
    "SpeakerEncoderEngine",
    "create_speaker_encoder_engine",
    "StreamingEngine",
    "create_streaming_engine",
    "DeforumEngine",
    "create_deforum_engine",
    "FOMMEngine",
    "create_fomm_engine",
    "SadTalkerEngine",
    "create_sadtalker_engine",
    "DeepFaceLabEngine",
    "create_deepfacelab_engine",
    "MoviePyEngine",
    "create_moviepy_engine",
    "FFmpegAIEngine",
    "create_ffmpeg_ai_engine",
    "VideoCreatorEngine",
    "create_video_creator_engine",
    "VoiceAIEngine",
    "create_voice_ai_engine",
    "LyrebirdEngine",
    "create_lyrebird_engine",
    "calculate_mos_score",
    "calculate_similarity",
    "calculate_naturalness",
    "calculate_snr",
    "detect_artifacts",
    "calculate_all_metrics",
    "clear_metrics_cache",
    "get_cache_stats",
    "QualityOptimizer",
    "optimize_synthesis_for_quality",
    "PROFESSIONAL_THRESHOLDS",
    "QUALITY_TIERS",
    "get_quality_preset",
    "get_engine_preset",
    "get_synthesis_params_from_preset",
    "list_quality_presets",
    "get_preset_description",
    "get_preset_target_metrics",
    "QUALITY_PRESETS",
    "ENGINE_PRESET_MAPPINGS",
    "QualityComparison",
    "compare_audio_samples",
    "EngineRouter",
    "router",
    "load_engine_manifest",
    "find_engine_manifests",
    "get_engine_entry_point",
    "get_engine_config_schema",
    "validate_engine_requirements",
    "EngineConfig",
    "get_engine_config",
    # ONNX utilities
    "convert_pytorch_to_onnx",
    "optimize_onnx_model",
    "quantize_onnx_model",
    "validate_onnx_model",
    "get_onnx_model_info",
    "ONNXInferenceEngine",
    "create_onnx_inference_engine",
    "HAS_ONNX",
]
