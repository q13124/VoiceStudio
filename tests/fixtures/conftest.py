"""
VoiceStudio Test Fixtures - Pytest Configuration.

Provides pytest fixtures that integrate all test data:
- Text samples and SSML
- Multi-language content
- Audio files and datasets
- Presets and configurations
- Workflow scenarios
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add fixtures directory to path
FIXTURES_DIR = Path(__file__).parent
sys.path.insert(0, str(FIXTURES_DIR))

# Import fixture modules
from datasets import (
    AUDIO_DIR,
    AUDIO_FILE_CONFIGS,
    BATCH_JOB_CONFIGS,
    DATASETS_DIR,
    SAMPLE_DATASETS,
    BatchJobConfig,
    TrainingDataset,
    generate_all_test_audio,
    generate_test_audio_file,
    get_batch_job_by_id,
    get_dataset_by_id,
)
from presets import (
    EFFECT_CHAIN_PRESETS,
    EXPORT_PRESETS,
    PROJECT_TEMPLATES,
    SYNTHESIS_PRESETS,
    TRAINING_PRESETS,
    EffectChainPreset,
    ExportPreset,
    ProjectTemplate,
    SynthesisPreset,
    TrainingPreset,
    get_effect_presets_by_category,
)
from test_data import (
    LANGUAGE_SAMPLES,
    SSML_SAMPLES,
    TEXT_SAMPLES,
    VOICE_PROFILES,
    LanguageSample,
    SSMLSample,
    TextSample,
    VoiceProfileConfig,
    get_all_supported_languages,
    get_effect_presets_by_category,
    get_language_sample,
    get_ssml_samples_by_category,
    get_text_samples_by_category,
    get_voice_profiles_by_engine,
)
from workflows import (
    ALL_WORKFLOWS,
    CLONING_WORKFLOWS,
    SYNTHESIS_WORKFLOWS,
    Workflow,
    WorkflowCategory,
    get_regression_test_workflows,
    get_smoke_test_workflows,
    get_workflow_by_id,
    get_workflows_by_priority,
)

# =============================================================================
# TEXT FIXTURES
# =============================================================================


@pytest.fixture
def text_samples() -> list[TextSample]:
    """All text samples."""
    return TEXT_SAMPLES


@pytest.fixture
def short_text_samples() -> list[TextSample]:
    """Short text samples (< 2 seconds)."""
    return get_text_samples_by_category("short")


@pytest.fixture
def medium_text_samples() -> list[TextSample]:
    """Medium text samples (2-10 seconds)."""
    return get_text_samples_by_category("medium")


@pytest.fixture
def long_text_samples() -> list[TextSample]:
    """Long text samples (> 10 seconds)."""
    return get_text_samples_by_category("long")


@pytest.fixture
def edge_case_samples() -> list[TextSample]:
    """Edge case text samples."""
    return get_text_samples_by_category("edge")


@pytest.fixture
def sample_text() -> str:
    """Simple sample text for basic tests."""
    return "Hello, this is a test of the voice synthesis system."


@pytest.fixture
def paragraph_text() -> str:
    """Longer paragraph for extended tests."""
    return TEXT_SAMPLES[5].text  # medium_paragraph


# =============================================================================
# SSML FIXTURES
# =============================================================================


@pytest.fixture
def ssml_samples() -> list[SSMLSample]:
    """All SSML samples."""
    return SSML_SAMPLES


@pytest.fixture
def basic_ssml_samples() -> list[SSMLSample]:
    """Basic SSML samples."""
    return get_ssml_samples_by_category("basic")


@pytest.fixture
def prosody_ssml_samples() -> list[SSMLSample]:
    """SSML samples with prosody controls."""
    return get_ssml_samples_by_category("prosody")


@pytest.fixture
def interpretation_ssml_samples() -> list[SSMLSample]:
    """SSML samples with say-as interpretation."""
    return get_ssml_samples_by_category("interpretation")


@pytest.fixture
def sample_ssml() -> str:
    """Simple SSML sample."""
    return '<speak>Hello, <emphasis level="strong">this is a test</emphasis>.</speak>'


# =============================================================================
# LANGUAGE FIXTURES
# =============================================================================


@pytest.fixture
def language_samples() -> list[LanguageSample]:
    """All language samples."""
    return LANGUAGE_SAMPLES


@pytest.fixture
def supported_languages() -> list[str]:
    """List of supported language codes."""
    return get_all_supported_languages()


@pytest.fixture
def english_samples() -> LanguageSample | None:
    """English (US) language samples."""
    return get_language_sample("en-US")


@pytest.fixture
def multi_language_texts() -> dict[str, str]:
    """Sample texts in multiple languages."""
    return {
        sample.language_code: sample.samples[0]["text"]
        for sample in LANGUAGE_SAMPLES
        if sample.samples
    }


# =============================================================================
# VOICE PROFILE FIXTURES
# =============================================================================


@pytest.fixture
def voice_profiles() -> list[VoiceProfileConfig]:
    """All voice profile configurations."""
    return VOICE_PROFILES


@pytest.fixture
def piper_profiles() -> list[VoiceProfileConfig]:
    """Piper engine profiles."""
    return get_voice_profiles_by_engine("piper")


@pytest.fixture
def xtts_profiles() -> list[VoiceProfileConfig]:
    """XTTS engine profiles."""
    return get_voice_profiles_by_engine("xtts")


@pytest.fixture
def default_profile() -> VoiceProfileConfig:
    """Default voice profile."""
    return VOICE_PROFILES[0]


# =============================================================================
# AUDIO FILE FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def audio_fixtures_dir() -> Path:
    """Path to audio fixtures directory."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    return AUDIO_DIR


@pytest.fixture(scope="session")
def generated_audio_files(audio_fixtures_dir) -> list[Path]:
    """Generate all test audio files (session-scoped for efficiency)."""
    return generate_all_test_audio()


@pytest.fixture
def short_audio_file(audio_fixtures_dir) -> Path:
    """Path to a short audio file."""
    config = AUDIO_FILE_CONFIGS[0]  # short_1s.wav
    return generate_test_audio_file(config, audio_fixtures_dir)


@pytest.fixture
def standard_audio_file(audio_fixtures_dir) -> Path:
    """Path to a standard audio file."""
    config = AUDIO_FILE_CONFIGS[3]  # standard_5s.wav
    return generate_test_audio_file(config, audio_fixtures_dir)


@pytest.fixture
def stereo_audio_file(audio_fixtures_dir) -> Path:
    """Path to a stereo audio file."""
    config = AUDIO_FILE_CONFIGS[10]  # stereo_5s.wav
    return generate_test_audio_file(config, audio_fixtures_dir)


@pytest.fixture
def silence_audio_file(audio_fixtures_dir) -> Path:
    """Path to a silent audio file."""
    config = AUDIO_FILE_CONFIGS[11]  # silence_3s.wav
    return generate_test_audio_file(config, audio_fixtures_dir)


# =============================================================================
# DATASET FIXTURES
# =============================================================================


@pytest.fixture
def sample_datasets() -> list[TrainingDataset]:
    """All sample datasets."""
    return SAMPLE_DATASETS


@pytest.fixture
def minimal_dataset() -> TrainingDataset:
    """Minimal dataset for quick testing."""
    return get_dataset_by_id("dataset_minimal")


@pytest.fixture
def small_dataset() -> TrainingDataset:
    """Small dataset for basic testing."""
    return get_dataset_by_id("dataset_small")


@pytest.fixture
def multi_speaker_dataset() -> TrainingDataset:
    """Multi-speaker dataset."""
    return get_dataset_by_id("dataset_multispeaker")


@pytest.fixture
def batch_job_configs() -> list[BatchJobConfig]:
    """All batch job configurations."""
    return BATCH_JOB_CONFIGS


@pytest.fixture
def batch_synthesis_job() -> BatchJobConfig:
    """Batch synthesis job configuration."""
    return get_batch_job_by_id("batch_synthesis_small")


# =============================================================================
# PRESET FIXTURES
# =============================================================================


@pytest.fixture
def synthesis_presets() -> list[SynthesisPreset]:
    """All synthesis presets."""
    return SYNTHESIS_PRESETS


@pytest.fixture
def effect_chain_presets() -> list[EffectChainPreset]:
    """All effect chain presets."""
    return EFFECT_CHAIN_PRESETS


@pytest.fixture
def training_presets() -> list[TrainingPreset]:
    """All training presets."""
    return TRAINING_PRESETS


@pytest.fixture
def export_presets() -> list[ExportPreset]:
    """All export presets."""
    return EXPORT_PRESETS


@pytest.fixture
def project_templates() -> list[ProjectTemplate]:
    """All project templates."""
    return PROJECT_TEMPLATES


@pytest.fixture
def default_synthesis_preset() -> SynthesisPreset:
    """Default synthesis preset."""
    return SYNTHESIS_PRESETS[0]


@pytest.fixture
def voice_enhancement_preset() -> EffectChainPreset:
    """Voice enhancement effect preset."""
    return get_effect_presets_by_category("voice")[0]


# =============================================================================
# WORKFLOW FIXTURES
# =============================================================================


@pytest.fixture
def all_workflows() -> list[Workflow]:
    """All workflow scenarios."""
    return ALL_WORKFLOWS


@pytest.fixture
def synthesis_workflows() -> list[Workflow]:
    """Synthesis workflow scenarios."""
    return SYNTHESIS_WORKFLOWS


@pytest.fixture
def cloning_workflows() -> list[Workflow]:
    """Voice cloning workflow scenarios."""
    return CLONING_WORKFLOWS


@pytest.fixture
def smoke_test_workflows() -> list[Workflow]:
    """Workflows suitable for smoke testing."""
    return get_smoke_test_workflows()


@pytest.fixture
def regression_workflows() -> list[Workflow]:
    """All workflows for regression testing (sorted by priority)."""
    return get_regression_test_workflows()


@pytest.fixture
def high_priority_workflows() -> list[Workflow]:
    """High priority workflows (priority >= 8)."""
    return get_workflows_by_priority(8)


@pytest.fixture
def basic_synthesis_workflow() -> Workflow:
    """Basic synthesis workflow."""
    return get_workflow_by_id("wf_synth_basic")


@pytest.fixture
def voice_cloning_workflow() -> Workflow:
    """Voice cloning wizard workflow."""
    return get_workflow_by_id("wf_clone_wizard")


# =============================================================================
# COMBINED FIXTURES
# =============================================================================


@pytest.fixture
def test_fixture_summary() -> dict[str, int]:
    """Summary of all available fixtures."""
    return {
        "text_samples": len(TEXT_SAMPLES),
        "ssml_samples": len(SSML_SAMPLES),
        "languages": len(LANGUAGE_SAMPLES),
        "voice_profiles": len(VOICE_PROFILES),
        "audio_configs": len(AUDIO_FILE_CONFIGS),
        "datasets": len(SAMPLE_DATASETS),
        "batch_jobs": len(BATCH_JOB_CONFIGS),
        "synthesis_presets": len(SYNTHESIS_PRESETS),
        "effect_presets": len(EFFECT_CHAIN_PRESETS),
        "training_presets": len(TRAINING_PRESETS),
        "export_presets": len(EXPORT_PRESETS),
        "project_templates": len(PROJECT_TEMPLATES),
        "workflows": len(ALL_WORKFLOWS),
    }


@pytest.fixture
def fixture_paths() -> dict[str, Path]:
    """Paths to fixture directories."""
    return {
        "fixtures": FIXTURES_DIR,
        "audio": AUDIO_DIR,
        "datasets": DATASETS_DIR,
    }


# =============================================================================
# PARAMETRIZE HELPERS
# =============================================================================


def pytest_generate_tests(metafunc):
    """Automatically parametrize tests based on fixture requirements."""

    # Parametrize text samples by category
    if "text_category" in metafunc.fixturenames:
        metafunc.parametrize("text_category", ["short", "medium", "long", "edge"])

    # Parametrize SSML categories
    if "ssml_category" in metafunc.fixturenames:
        metafunc.parametrize(
            "ssml_category", ["basic", "prosody", "timing", "emphasis", "interpretation"]
        )

    # Parametrize languages
    if "language_code" in metafunc.fixturenames:
        metafunc.parametrize("language_code", get_all_supported_languages())

    # Parametrize engines
    if "engine_name" in metafunc.fixturenames:
        metafunc.parametrize("engine_name", ["piper", "xtts", "bark", "openvoice", "chatterbox"])

    # Parametrize workflow categories
    if "workflow_category" in metafunc.fixturenames:
        metafunc.parametrize("workflow_category", [c.value for c in WorkflowCategory])


# =============================================================================
# MARKERS
# =============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "synthesis: Tests for TTS synthesis")
    config.addinivalue_line("markers", "transcription: Tests for STT transcription")
    config.addinivalue_line("markers", "cloning: Tests for voice cloning")
    config.addinivalue_line("markers", "effects: Tests for audio effects")
    config.addinivalue_line("markers", "batch: Tests for batch processing")
    config.addinivalue_line("markers", "training: Tests for model training")
    config.addinivalue_line("markers", "workflow: Workflow-based tests")
    config.addinivalue_line("markers", "multilang: Multi-language tests")
    config.addinivalue_line("markers", "ssml: SSML markup tests")
    config.addinivalue_line("markers", "edge_case: Edge case tests")


if __name__ == "__main__":
    print("VoiceStudio Test Fixtures - Pytest Configuration")
    print("=" * 50)
    print("\nAvailable fixtures:")

    summary = {
        "text_samples": len(TEXT_SAMPLES),
        "ssml_samples": len(SSML_SAMPLES),
        "languages": len(LANGUAGE_SAMPLES),
        "voice_profiles": len(VOICE_PROFILES),
        "audio_configs": len(AUDIO_FILE_CONFIGS),
        "datasets": len(SAMPLE_DATASETS),
        "batch_jobs": len(BATCH_JOB_CONFIGS),
        "synthesis_presets": len(SYNTHESIS_PRESETS),
        "effect_presets": len(EFFECT_CHAIN_PRESETS),
        "training_presets": len(TRAINING_PRESETS),
        "export_presets": len(EXPORT_PRESETS),
        "project_templates": len(PROJECT_TEMPLATES),
        "workflows": len(ALL_WORKFLOWS),
    }

    for key, count in summary.items():
        print(f"  {key}: {count}")

    print("\n" + "=" * 50)
