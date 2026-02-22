"""
Unit tests for Build Provenance.

Tests the Provenance, ProvenanceGenerator, and related classes.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.plugins.supply_chain.provenance import (
    BuilderInfo,
    BuildType,
    InputArtifact,
    Provenance,
    ProvenanceGenerator,
    ProvenanceVersion,
    SourceInfo,
    generate_provenance,
    load_provenance,
    verify_provenance_digest,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """Create a temporary plugin directory."""
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()

    # Create plugin files
    (plugin_dir / "plugin.json").write_text('{"name": "test", "version": "1.0.0"}')
    (plugin_dir / "main.py").write_text("print('hello')")
    (plugin_dir / "requirements.txt").write_text("requests==2.28.0\n")

    return plugin_dir


@pytest.fixture
def sample_package(tmp_path):
    """Create a sample package file."""
    package_path = tmp_path / "test_plugin-1.0.0.vspkg"
    package_path.write_bytes(b"fake package content")
    return package_path


@pytest.fixture
def sample_builder_info():
    """Create a sample builder info."""
    return BuilderInfo(
        hostname="test-machine",
        machine_id="abc123",
        os_name="Windows",
        os_version="10.0.19041",
        os_release="10",
        python_version="3.9.13",
        python_implementation="CPython",
        username="testuser",
    )


@pytest.fixture
def sample_source_info():
    """Create a sample source info."""
    return SourceInfo(
        repository="https://github.com/test/repo",
        commit="abc123def456",
        branch="main",
        tag="v1.0.0",
        dirty=False,
    )


@pytest.fixture
def sample_provenance(sample_builder_info, sample_source_info):
    """Create a sample provenance."""
    return Provenance(
        provenance_id="prov-123",
        subject_name="test-plugin",
        subject_version="1.0.0",
        subject_digest={"sha256": "abc123"},
        build_type=BuildType.DEVELOPMENT,
        build_started_at="2025-01-01T00:00:00+00:00",
        build_finished_at="2025-01-01T00:01:00+00:00",
        build_duration_ms=60000,
        builder=sample_builder_info,
        source=sample_source_info,
    )


# =============================================================================
# Test BuildType Enum
# =============================================================================


class TestBuildType:
    """Tests for BuildType enum."""

    def test_all_types_defined(self):
        """Test that all build types are defined."""
        expected = ["DEVELOPMENT", "CI", "RELEASE", "UNKNOWN"]
        for name in expected:
            assert hasattr(BuildType, name)

    def test_type_values(self):
        """Test build type values."""
        assert BuildType.DEVELOPMENT.value == "development"
        assert BuildType.CI.value == "ci"
        assert BuildType.RELEASE.value == "release"
        assert BuildType.UNKNOWN.value == "unknown"


# =============================================================================
# Test ProvenanceVersion Enum
# =============================================================================


class TestProvenanceVersion:
    """Tests for ProvenanceVersion enum."""

    def test_version_defined(self):
        """Test that version is defined."""
        assert hasattr(ProvenanceVersion, "V1")
        assert ProvenanceVersion.V1.value == "1.0"


# =============================================================================
# Test SourceInfo
# =============================================================================


class TestSourceInfo:
    """Tests for SourceInfo dataclass."""

    def test_basic_creation(self, sample_source_info):
        """Test creating source info."""
        info = sample_source_info

        assert info.repository == "https://github.com/test/repo"
        assert info.commit == "abc123def456"
        assert info.branch == "main"
        assert info.tag == "v1.0.0"
        assert info.dirty is False

    def test_to_dict(self, sample_source_info):
        """Test converting to dictionary."""
        data = sample_source_info.to_dict()

        assert data["repository"] == "https://github.com/test/repo"
        assert data["commit"] == "abc123def456"
        assert data["branch"] == "main"

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "repository": "https://example.com/repo",
            "commit": "xyz789",
            "branch": "develop",
            "tag": None,
            "dirty": True,
        }

        info = SourceInfo.from_dict(data)

        assert info.repository == "https://example.com/repo"
        assert info.commit == "xyz789"
        assert info.dirty is True


# =============================================================================
# Test BuilderInfo
# =============================================================================


class TestBuilderInfo:
    """Tests for BuilderInfo dataclass."""

    def test_basic_creation(self, sample_builder_info):
        """Test creating builder info."""
        info = sample_builder_info

        assert info.hostname == "test-machine"
        assert info.os_name == "Windows"
        assert info.python_version == "3.9.13"

    def test_to_dict(self, sample_builder_info):
        """Test converting to dictionary."""
        data = sample_builder_info.to_dict()

        assert data["hostname"] == "test-machine"
        assert data["os"]["name"] == "Windows"
        assert data["python"]["version"] == "3.9.13"

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "hostname": "build-server",
            "machine_id": "xyz789",
            "os": {
                "name": "Linux",
                "version": "5.15.0",
                "release": "ubuntu",
            },
            "python": {
                "version": "3.10.0",
                "implementation": "CPython",
            },
            "username": "builder",
            "ci_platform": "github-actions",
            "ci_run_id": "12345",
        }

        info = BuilderInfo.from_dict(data)

        assert info.hostname == "build-server"
        assert info.os_name == "Linux"
        assert info.ci_platform == "github-actions"


# =============================================================================
# Test InputArtifact
# =============================================================================


class TestInputArtifact:
    """Tests for InputArtifact dataclass."""

    def test_basic_creation(self):
        """Test creating input artifact."""
        artifact = InputArtifact(
            name="requirements.txt",
            path="requirements.txt",
            digest={"sha256": "abc123"},
        )

        assert artifact.name == "requirements.txt"
        assert artifact.digest["sha256"] == "abc123"

    def test_to_dict(self):
        """Test converting to dictionary."""
        artifact = InputArtifact(
            name="main.py",
            path="src/main.py",
            digest={"sha256": "def456"},
        )

        data = artifact.to_dict()

        assert data["name"] == "main.py"
        assert data["path"] == "src/main.py"

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "name": "config.json",
            "path": "config/config.json",
            "digest": {"sha256": "ghi789"},
        }

        artifact = InputArtifact.from_dict(data)

        assert artifact.name == "config.json"


# =============================================================================
# Test Provenance
# =============================================================================


class TestProvenance:
    """Tests for Provenance dataclass."""

    def test_basic_creation(self, sample_provenance):
        """Test creating provenance."""
        prov = sample_provenance

        assert prov.subject_name == "test-plugin"
        assert prov.subject_version == "1.0.0"
        assert prov.build_type == BuildType.DEVELOPMENT

    def test_auto_id_generation(self):
        """Test that provenance ID is auto-generated."""
        prov = Provenance()

        assert prov.provenance_id != ""
        assert len(prov.provenance_id) > 0

    def test_to_dict(self, sample_provenance):
        """Test converting to dictionary."""
        data = sample_provenance.to_dict()

        assert data["subject"]["name"] == "test-plugin"
        assert data["build"]["type"] == "development"
        assert "builder" in data
        assert "source" in data

    def test_to_json(self, sample_provenance):
        """Test converting to JSON."""
        json_str = sample_provenance.to_json()
        parsed = json.loads(json_str)

        assert parsed["subject"]["name"] == "test-plugin"

    def test_save(self, sample_provenance, tmp_path):
        """Test saving provenance to file."""
        output_path = tmp_path / "provenance.json"
        sample_provenance.save(output_path)

        assert output_path.exists()
        content = json.loads(output_path.read_text())
        assert content["subject"]["name"] == "test-plugin"

    def test_from_dict(self, sample_builder_info, sample_source_info):
        """Test creating from dictionary."""
        data = {
            "provenance_id": "prov-456",
            "spec_version": "1.0",
            "subject": {
                "name": "another-plugin",
                "version": "2.0.0",
                "digest": {"sha256": "xyz789"},
            },
            "build": {
                "type": "release",
                "started_at": "2025-02-01T00:00:00+00:00",
                "finished_at": "2025-02-01T00:05:00+00:00",
                "duration_ms": 300000,
            },
            "builder": sample_builder_info.to_dict(),
            "source": sample_source_info.to_dict(),
            "input_artifacts": [],
            "build_config": {"key": "value"},
            "reproducibility": {
                "reproducible": True,
                "notes": "Deterministic build",
            },
            "metadata": {"custom": "data"},
        }

        prov = Provenance.from_dict(data)

        assert prov.subject_name == "another-plugin"
        assert prov.build_type == BuildType.RELEASE
        assert prov.reproducible is True

    def test_load(self, sample_provenance, tmp_path):
        """Test loading provenance from file."""
        output_path = tmp_path / "provenance.json"
        sample_provenance.save(output_path)

        loaded = Provenance.load(output_path)

        assert loaded.subject_name == sample_provenance.subject_name
        assert loaded.provenance_id == sample_provenance.provenance_id


# =============================================================================
# Test ProvenanceGenerator
# =============================================================================


class TestProvenanceGenerator:
    """Tests for ProvenanceGenerator class."""

    def test_basic_creation(self, temp_plugin_dir):
        """Test creating a generator."""
        generator = ProvenanceGenerator(temp_plugin_dir)

        assert generator.plugin_path == temp_plugin_dir
        assert generator.package_name == "test_plugin"

    def test_custom_name_version(self, temp_plugin_dir):
        """Test creating with custom name and version."""
        generator = ProvenanceGenerator(
            temp_plugin_dir,
            package_name="custom-plugin",
            package_version="2.5.0",
        )

        assert generator.package_name == "custom-plugin"
        assert generator.package_version == "2.5.0"

    def test_start_finish_build(self, temp_plugin_dir):
        """Test build timing."""
        generator = ProvenanceGenerator(temp_plugin_dir)

        generator.start_build()
        assert generator._build_started is not None

        generator.finish_build()
        assert generator._build_finished is not None
        assert generator._build_finished >= generator._build_started

    @patch("backend.plugins.supply_chain.provenance.subprocess.run")
    def test_generate_basic(self, mock_run, temp_plugin_dir):
        """Test basic provenance generation."""
        # Mock git commands returning no git repo
        mock_run.return_value = MagicMock(returncode=1)

        generator = ProvenanceGenerator(
            temp_plugin_dir,
            package_name="test-plugin",
            package_version="1.0.0",
        )

        prov = generator.generate()

        assert prov.subject_name == "test-plugin"
        assert prov.subject_version == "1.0.0"
        assert prov.builder.os_name != ""
        assert prov.builder.python_version != ""

    @patch("backend.plugins.supply_chain.provenance.subprocess.run")
    def test_generate_with_package(self, mock_run, temp_plugin_dir, sample_package):
        """Test generating provenance with package digest."""
        mock_run.return_value = MagicMock(returncode=1)

        generator = ProvenanceGenerator(temp_plugin_dir)
        prov = generator.generate(package_path=sample_package)

        assert "sha256" in prov.subject_digest
        assert "sha512" in prov.subject_digest

    @patch("backend.plugins.supply_chain.provenance.subprocess.run")
    def test_generate_with_build_type(self, mock_run, temp_plugin_dir):
        """Test generating with different build types."""
        mock_run.return_value = MagicMock(returncode=1)

        generator = ProvenanceGenerator(temp_plugin_dir)
        prov = generator.generate(build_type=BuildType.RELEASE)

        assert prov.build_type == BuildType.RELEASE

    @patch("backend.plugins.supply_chain.provenance.subprocess.run")
    def test_generate_collects_input_artifacts(self, mock_run, temp_plugin_dir):
        """Test that input artifacts are collected."""
        mock_run.return_value = MagicMock(returncode=1)

        generator = ProvenanceGenerator(temp_plugin_dir)
        prov = generator.generate()

        # Should have collected plugin.json, main.py, requirements.txt
        artifact_names = [a.name for a in prov.input_artifacts]
        assert "plugin.json" in artifact_names
        assert "main.py" in artifact_names
        assert "requirements.txt" in artifact_names

    def test_anonymization(self, temp_plugin_dir):
        """Test anonymization of sensitive data."""
        generator = ProvenanceGenerator(temp_plugin_dir, anonymize=True)

        # The hostname should be hashed when anonymized
        anonymized = generator._maybe_anonymize("test-hostname")
        assert anonymized != "test-hostname"
        assert len(anonymized) == 12  # SHA256 truncated to 12 chars


class TestProvenanceGeneratorGitIntegration:
    """Tests for git integration in ProvenanceGenerator."""

    @patch("backend.plugins.supply_chain.provenance.subprocess.run")
    def test_git_info_collected(self, mock_run, temp_plugin_dir):
        """Test that git info is collected when available."""

        # Mock git commands - check the exact command list
        def mock_git_command(*args, **kwargs):
            cmd = args[0]
            mock_result = MagicMock()

            # Convert list to string for easier matching
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)

            if "--is-inside-work-tree" in cmd_str:
                mock_result.returncode = 0
                mock_result.stdout = "true"
            elif "--abbrev-ref" in cmd_str:
                # Branch name - this must come before general HEAD check
                mock_result.returncode = 0
                mock_result.stdout = "main"
            elif "rev-parse" in cmd_str and "HEAD" in cmd_str:
                # Commit hash
                mock_result.returncode = 0
                mock_result.stdout = "abc123def456"
            elif "remote" in cmd_str:
                mock_result.returncode = 0
                mock_result.stdout = "https://github.com/test/repo"
            elif "status" in cmd_str:
                mock_result.returncode = 0
                mock_result.stdout = ""
            elif "describe" in cmd_str:
                mock_result.returncode = 1  # No tag
                mock_result.stdout = ""
            else:
                mock_result.returncode = 1
                mock_result.stdout = ""

            return mock_result

        mock_run.side_effect = mock_git_command

        generator = ProvenanceGenerator(temp_plugin_dir)
        prov = generator.generate()

        assert prov.source.commit == "abc123def456"
        assert prov.source.branch == "main"

    @patch("backend.plugins.supply_chain.provenance.subprocess.run")
    def test_dirty_detection(self, mock_run, temp_plugin_dir):
        """Test dirty working tree detection."""

        def mock_git_command(*args, **kwargs):
            cmd = args[0]
            mock_result = MagicMock()

            if "rev-parse" in cmd and "--is-inside-work-tree" in cmd:
                mock_result.returncode = 0
            elif "status" in cmd and "--porcelain" in cmd:
                mock_result.returncode = 0
                mock_result.stdout = "M modified.py"  # Dirty
            else:
                mock_result.returncode = 0
                mock_result.stdout = ""

            return mock_result

        mock_run.side_effect = mock_git_command

        generator = ProvenanceGenerator(temp_plugin_dir)
        prov = generator.generate()

        assert prov.source.dirty is True


class TestProvenanceGeneratorCIDetection:
    """Tests for CI environment detection."""

    def test_github_actions_detection(self, temp_plugin_dir):
        """Test GitHub Actions detection."""
        with patch.dict("os.environ", {"GITHUB_ACTIONS": "true", "GITHUB_RUN_ID": "12345"}):
            generator = ProvenanceGenerator(temp_plugin_dir)
            ci_platform, ci_run_id = generator._detect_ci_environment()

            assert ci_platform == "github-actions"
            assert ci_run_id == "12345"

    def test_gitlab_ci_detection(self, temp_plugin_dir):
        """Test GitLab CI detection."""
        with patch.dict("os.environ", {"GITLAB_CI": "true", "CI_JOB_ID": "67890"}, clear=False):
            generator = ProvenanceGenerator(temp_plugin_dir)
            ci_platform, ci_run_id = generator._detect_ci_environment()

            assert ci_platform == "gitlab-ci"
            assert ci_run_id == "67890"

    def test_no_ci_detection(self, temp_plugin_dir):
        """Test when not in CI environment."""
        # Clear CI-related env vars
        env = {
            k: v
            for k, v in os.environ.items()
            if not any(
                ci in k.upper()
                for ci in ["CI", "GITHUB", "GITLAB", "JENKINS", "TRAVIS", "TF_BUILD", "CIRCLE"]
            )
        }

        with patch.dict("os.environ", env, clear=True):
            generator = ProvenanceGenerator(temp_plugin_dir)
            ci_platform, ci_run_id = generator._detect_ci_environment()

            assert ci_platform is None
            assert ci_run_id is None


# =============================================================================
# Test Convenience Functions
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    @patch("backend.plugins.supply_chain.provenance.subprocess.run")
    def test_generate_provenance(self, mock_run, temp_plugin_dir):
        """Test generate_provenance function."""
        mock_run.return_value = MagicMock(returncode=1)

        prov = generate_provenance(
            plugin_path=temp_plugin_dir,
            package_name="my-plugin",
            package_version="1.0.0",
        )

        assert prov.subject_name == "my-plugin"
        assert prov.subject_version == "1.0.0"

    def test_load_provenance(self, sample_provenance, tmp_path):
        """Test load_provenance function."""
        output_path = tmp_path / "provenance.json"
        sample_provenance.save(output_path)

        loaded = load_provenance(output_path)

        assert loaded.subject_name == sample_provenance.subject_name

    def test_verify_provenance_digest_success(self, sample_package, tmp_path):
        """Test successful digest verification."""
        # Create provenance with correct digest
        import hashlib

        content = sample_package.read_bytes()
        digest = hashlib.sha256(content).hexdigest()

        prov = Provenance(
            subject_name="test",
            subject_version="1.0",
            subject_digest={"sha256": digest},
        )

        result = verify_provenance_digest(prov, sample_package)

        assert result is True

    def test_verify_provenance_digest_failure(self, sample_package, tmp_path):
        """Test failed digest verification."""
        prov = Provenance(
            subject_name="test",
            subject_version="1.0",
            subject_digest={"sha256": "wrong_digest"},
        )

        result = verify_provenance_digest(prov, sample_package)

        assert result is False

    def test_verify_provenance_file_not_found(self, tmp_path):
        """Test verification with missing file."""
        prov = Provenance(
            subject_name="test",
            subject_version="1.0",
            subject_digest={"sha256": "abc123"},
        )

        result = verify_provenance_digest(prov, tmp_path / "nonexistent.vspkg")

        assert result is False

    def test_verify_provenance_no_digest(self, sample_package):
        """Test verification with no digest in provenance."""
        prov = Provenance(
            subject_name="test",
            subject_version="1.0",
            subject_digest={},
        )

        result = verify_provenance_digest(prov, sample_package)

        assert result is False


# Import os for CI detection tests
import os
