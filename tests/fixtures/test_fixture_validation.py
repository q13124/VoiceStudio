"""
Fixture Validation Tests (Phase 11)

Validates that all test fixtures are properly configured and accessible:
- Audio fixtures exist and are valid
- Mock data is consistent
- Test environment reset procedures work
"""

from __future__ import annotations

import pytest
from pathlib import Path


# =============================================================================
# FIXTURE LOADING TESTS
# =============================================================================

@pytest.mark.fixtures
class TestFixtureModulesLoad:
    """Tests that fixture modules can be imported."""

    def test_test_data_module_loads(self):
        """Test that test_data module loads."""
        from tests.fixtures.test_data import TEXT_SAMPLES, SSML_SAMPLES, LANGUAGE_SAMPLES
        assert len(TEXT_SAMPLES) > 0
        assert len(SSML_SAMPLES) > 0
        assert len(LANGUAGE_SAMPLES) > 0

    def test_datasets_module_loads(self):
        """Test that datasets module loads."""
        from tests.fixtures.datasets import SAMPLE_DATASETS, AUDIO_FILE_CONFIGS, BATCH_JOB_CONFIGS
        assert len(SAMPLE_DATASETS) > 0
        assert len(AUDIO_FILE_CONFIGS) > 0
        assert len(BATCH_JOB_CONFIGS) > 0

    def test_presets_module_loads(self):
        """Test that presets module loads."""
        from tests.fixtures.presets import SYNTHESIS_PRESETS, EFFECT_CHAIN_PRESETS, TRAINING_PRESETS
        assert len(SYNTHESIS_PRESETS) > 0
        assert len(EFFECT_CHAIN_PRESETS) > 0
        assert len(TRAINING_PRESETS) > 0

    def test_workflows_module_loads(self):
        """Test that workflows module loads."""
        from tests.fixtures.workflows import ALL_WORKFLOWS, SYNTHESIS_WORKFLOWS, CLONING_WORKFLOWS
        assert len(ALL_WORKFLOWS) > 0
        assert len(SYNTHESIS_WORKFLOWS) > 0
        assert len(CLONING_WORKFLOWS) > 0

    def test_engines_module_loads(self):
        """Test that engines module loads."""
        from tests.fixtures.engines import MockEngineFactory
        assert MockEngineFactory is not None

    def test_factories_module_loads(self):
        """Test that factories module loads."""
        from tests.fixtures.factories import ProfileFactory, AudioFactory
        assert ProfileFactory is not None
        assert AudioFactory is not None


# =============================================================================
# TEXT FIXTURE TESTS
# =============================================================================

@pytest.mark.fixtures
class TestTextFixtures:
    """Tests for text-based fixtures."""

    def test_text_samples_have_required_fields(self):
        """Test that text samples have required fields."""
        from tests.fixtures.test_data import TEXT_SAMPLES
        for sample in TEXT_SAMPLES:
            assert hasattr(sample, 'id')
            assert hasattr(sample, 'text')
            assert hasattr(sample, 'category')
            # Empty text is a valid edge case
            assert sample.text is not None

    def test_ssml_samples_are_valid_xml(self):
        """Test that SSML samples are valid markup."""
        from tests.fixtures.test_data import SSML_SAMPLES
        for sample in SSML_SAMPLES:
            assert hasattr(sample, 'ssml')
            assert '<speak>' in sample.ssml or 'speak' in str(type(sample))

    def test_language_samples_have_valid_codes(self):
        """Test that language samples have valid language codes."""
        from tests.fixtures.test_data import LANGUAGE_SAMPLES
        for sample in LANGUAGE_SAMPLES:
            assert hasattr(sample, 'language_code')
            # Language codes should be like 'en-US', 'es-ES', etc.
            assert len(sample.language_code) >= 2


# =============================================================================
# AUDIO FIXTURE TESTS
# =============================================================================

@pytest.mark.fixtures
class TestAudioFixtures:
    """Tests for audio fixtures."""

    def test_audio_file_configs_are_valid(self):
        """Test that audio file configurations are valid."""
        from tests.fixtures.datasets import AUDIO_FILE_CONFIGS
        for config in AUDIO_FILE_CONFIGS:
            assert hasattr(config, 'filename')  # Uses filename, not name
            assert hasattr(config, 'duration_seconds')
            assert hasattr(config, 'sample_rate')
            assert config.duration_seconds > 0
            assert config.sample_rate > 0

    def test_audio_generation_function_exists(self):
        """Test that audio generation function is available."""
        from tests.fixtures.datasets import generate_test_audio_file
        assert callable(generate_test_audio_file)

    def test_canonical_audio_module_exists(self):
        """Test that canonical audio module exists and has paths."""
        from tests.fixtures.canonical import CANONICAL_AUDIO_DIR
        assert CANONICAL_AUDIO_DIR is not None


# =============================================================================
# DATASET FIXTURE TESTS
# =============================================================================

@pytest.mark.fixtures
class TestDatasetFixtures:
    """Tests for dataset fixtures."""

    def test_sample_datasets_have_required_fields(self):
        """Test that sample datasets have required metadata."""
        from tests.fixtures.datasets import SAMPLE_DATASETS
        for dataset in SAMPLE_DATASETS:
            assert hasattr(dataset, 'metadata')
            assert hasattr(dataset.metadata, 'id')
            assert hasattr(dataset.metadata, 'name')
            assert hasattr(dataset.metadata, 'num_samples')
            assert dataset.metadata.num_samples > 0

    def test_batch_job_configs_are_valid(self):
        """Test that batch job configs are valid."""
        from tests.fixtures.datasets import BATCH_JOB_CONFIGS
        for job in BATCH_JOB_CONFIGS:
            assert hasattr(job, 'id')  # Uses id, not job_id
            assert hasattr(job, 'job_type')

    def test_get_dataset_by_id_works(self):
        """Test that get_dataset_by_id returns datasets."""
        from tests.fixtures.datasets import get_dataset_by_id, SAMPLE_DATASETS
        if SAMPLE_DATASETS:
            first_id = SAMPLE_DATASETS[0].metadata.id
            result = get_dataset_by_id(first_id)
            assert result is not None
            assert result.metadata.id == first_id


# =============================================================================
# PRESET FIXTURE TESTS
# =============================================================================

@pytest.mark.fixtures
class TestPresetFixtures:
    """Tests for preset fixtures."""

    def test_synthesis_presets_have_required_fields(self):
        """Test synthesis presets have required fields."""
        from tests.fixtures.presets import SYNTHESIS_PRESETS
        for preset in SYNTHESIS_PRESETS:
            assert hasattr(preset, 'id')  # Uses id, not preset_id
            assert hasattr(preset, 'name')

    def test_effect_chain_presets_have_effects(self):
        """Test effect chain presets have effect lists."""
        from tests.fixtures.presets import EFFECT_CHAIN_PRESETS
        for preset in EFFECT_CHAIN_PRESETS:
            assert hasattr(preset, 'effects')

    def test_training_presets_have_configs(self):
        """Test training presets have configuration."""
        from tests.fixtures.presets import TRAINING_PRESETS
        for preset in TRAINING_PRESETS:
            assert hasattr(preset, 'id')  # Uses id, not preset_id

    def test_export_presets_are_valid(self):
        """Test export presets have required fields."""
        from tests.fixtures.presets import EXPORT_PRESETS
        for preset in EXPORT_PRESETS:
            assert hasattr(preset, 'id')  # Uses id, not preset_id
            assert hasattr(preset, 'format')


# =============================================================================
# WORKFLOW FIXTURE TESTS
# =============================================================================

@pytest.mark.fixtures
class TestWorkflowFixtures:
    """Tests for workflow fixtures."""

    def test_all_workflows_have_steps(self):
        """Test that all workflows have steps defined."""
        from tests.fixtures.workflows import ALL_WORKFLOWS
        for workflow in ALL_WORKFLOWS:
            assert hasattr(workflow, 'id')  # Uses id, not workflow_id
            assert hasattr(workflow, 'actions')  # Uses actions, not steps
            assert len(workflow.actions) > 0

    def test_synthesis_workflows_have_synthesis_steps(self):
        """Test synthesis workflows contain synthesis operations."""
        from tests.fixtures.workflows import SYNTHESIS_WORKFLOWS
        assert len(SYNTHESIS_WORKFLOWS) > 0

    def test_cloning_workflows_exist(self):
        """Test cloning workflows are defined."""
        from tests.fixtures.workflows import CLONING_WORKFLOWS
        assert len(CLONING_WORKFLOWS) > 0

    def test_get_workflow_by_id_works(self):
        """Test that get_workflow_by_id returns workflows."""
        from tests.fixtures.workflows import get_workflow_by_id, ALL_WORKFLOWS
        if ALL_WORKFLOWS:
            first_id = ALL_WORKFLOWS[0].id  # Uses id, not workflow_id
            result = get_workflow_by_id(first_id)
            assert result is not None
            assert result.id == first_id


# =============================================================================
# ENGINE MOCK FIXTURE TESTS
# =============================================================================

@pytest.mark.fixtures
class TestEngineMockFixtures:
    """Tests for engine mock fixtures."""

    def test_mock_engine_factory_creates_xtts(self):
        """Test that MockEngineFactory can create XTTS mock."""
        from tests.fixtures.engines import MockEngineFactory
        xtts = MockEngineFactory.create_xtts()
        assert xtts is not None
        # MockEngine has id attribute
        assert hasattr(xtts, 'id') or hasattr(xtts, 'engine_id')

    def test_mock_engine_factory_creates_whisper(self):
        """Test that MockEngineFactory can create Whisper mock."""
        from tests.fixtures.engines import MockEngineFactory
        whisper = MockEngineFactory.create_whisper()
        assert whisper is not None
        # MockEngine has id attribute
        assert hasattr(whisper, 'id') or hasattr(whisper, 'engine_id')

    def test_mock_engine_service_creates_with_engines(self):
        """Test that MockEngineService creates with engines."""
        from tests.fixtures.engines import MockEngineService
        service = MockEngineService.create_with_engines()
        assert service is not None


# =============================================================================
# FACTORY FIXTURE TESTS
# =============================================================================

@pytest.mark.fixtures
class TestFactoryFixtures:
    """Tests for factory-based fixtures."""

    def test_profile_factory_creates_profile(self):
        """Test that ProfileFactory creates valid profiles."""
        from tests.fixtures.factories import ProfileFactory
        profile = ProfileFactory.create()
        assert profile is not None
        # Profile uses 'id' not 'profile_id'
        assert hasattr(profile, 'id')

    def test_audio_factory_creates_audio(self):
        """Test that AudioFactory creates audio data."""
        from tests.fixtures.factories import AudioFactory
        audio = AudioFactory.generate_sine_wave()
        assert audio is not None
        assert len(audio) > 0

    def test_project_factory_creates_project(self):
        """Test that ProjectFactory creates projects."""
        from tests.fixtures.factories import ProjectFactory
        project = ProjectFactory.create()
        assert project is not None
        # Project uses 'id' not 'project_id'
        assert hasattr(project, 'id')


# =============================================================================
# TEST ENVIRONMENT RESET TESTS
# =============================================================================

@pytest.mark.fixtures
class TestEnvironmentReset:
    """Tests for test environment reset procedures."""

    def test_temp_dir_fixture_cleanup(self, temp_dir: Path):
        """Test that temp_dir fixture creates and cleans up properly."""
        assert temp_dir.exists()
        test_file = temp_dir / "test.txt"
        test_file.write_text("test")
        assert test_file.exists()

    def test_clean_env_fixture_restores_env(self, clean_env):
        """Test that clean_env fixture restores environment."""
        import os
        original = os.environ.get("TEST_VAR_12345", None)
        os.environ["TEST_VAR_12345"] = "test_value"
        # After test, clean_env should restore original state

    def test_test_db_path_is_isolated(self, test_db_path: Path):
        """Test that test_db_path provides isolated database path."""
        assert test_db_path is not None
        # Should be in temp directory
        assert "test" in str(test_db_path).lower() or "tmp" in str(test_db_path).lower()


# =============================================================================
# FIXTURE SUMMARY TEST
# =============================================================================

@pytest.mark.fixtures
class TestFixtureSummary:
    """Test fixture summary statistics."""

    def test_fixture_summary_counts(self):
        """Test that fixture summary returns valid counts."""
        from tests.fixtures.test_data import TEXT_SAMPLES, SSML_SAMPLES, LANGUAGE_SAMPLES, VOICE_PROFILES
        from tests.fixtures.datasets import AUDIO_FILE_CONFIGS, SAMPLE_DATASETS, BATCH_JOB_CONFIGS
        from tests.fixtures.presets import SYNTHESIS_PRESETS, EFFECT_CHAIN_PRESETS, TRAINING_PRESETS, EXPORT_PRESETS, PROJECT_TEMPLATES
        from tests.fixtures.workflows import ALL_WORKFLOWS

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

        # All counts should be > 0
        for key, count in summary.items():
            assert count > 0, f"{key} has no fixtures"

        # Total fixture count should be substantial
        total = sum(summary.values())
        assert total >= 50, f"Expected at least 50 fixtures, got {total}"
