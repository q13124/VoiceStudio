"""
CI Configuration Validation Tests.

Tests for CI/CD infrastructure:
- Pre-commit hooks exist and are configured
- GitHub Actions workflows are valid
- CI pipeline stages are configured

Phase 10: CI Hardening
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

# Pytest markers
pytestmark = [
    pytest.mark.ci,
]


@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def pre_commit_config(project_root: Path) -> dict:
    """Load pre-commit configuration."""
    config_path = project_root / ".pre-commit-config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}


@pytest.fixture
def workflows_dir(project_root: Path) -> Path:
    """Get the GitHub workflows directory."""
    return project_root / ".github" / "workflows"


class TestPreCommitHooksExist:
    """Tests that required pre-commit hooks exist."""

    def test_pre_commit_config_exists(self, project_root: Path):
        """Test that .pre-commit-config.yaml exists."""
        config = project_root / ".pre-commit-config.yaml"
        assert config.exists(), f"Pre-commit config not found: {config}"

    def test_check_secrets_hook_exists(self, project_root: Path):
        """Test that check_secrets.py hook exists."""
        hook = project_root / "scripts" / "hooks" / "check_secrets.py"
        assert hook.exists(), f"Secrets check hook not found: {hook}"

    def test_check_large_files_hook_exists(self, project_root: Path):
        """Test that check_large_files.py hook exists."""
        hook = project_root / "scripts" / "hooks" / "check_large_files.py"
        assert hook.exists(), f"Large files check hook not found: {hook}"

    def test_check_conflict_markers_hook_exists(self, project_root: Path):
        """Test that check_conflict_markers.py hook exists."""
        hook = project_root / "scripts" / "hooks" / "check_conflict_markers.py"
        assert hook.exists(), f"Conflict markers check hook not found: {hook}"

    def test_check_xaml_nesting_hook_exists(self, project_root: Path):
        """Test that check_xaml_nesting.py hook exists."""
        hook = project_root / "scripts" / "hooks" / "check_xaml_nesting.py"
        assert hook.exists(), f"XAML nesting check hook not found: {hook}"


class TestPreCommitConfiguration:
    """Tests for pre-commit configuration content."""

    def test_repos_defined(self, pre_commit_config: dict):
        """Test that repos are defined in pre-commit config."""
        assert "repos" in pre_commit_config, "No repos defined in pre-commit config"
        assert len(pre_commit_config["repos"]) > 0, "Empty repos in pre-commit config"

    def test_security_hooks_configured(self, pre_commit_config: dict):
        """Test that security hooks are configured."""
        all_hooks = []
        for repo in pre_commit_config.get("repos", []):
            for hook in repo.get("hooks", []):
                all_hooks.append(hook.get("id", ""))

        assert "check-secrets" in all_hooks, "check-secrets hook not configured"

    def test_python_linting_configured(self, pre_commit_config: dict):
        """Test that Python linting is configured."""
        all_hooks = []
        for repo in pre_commit_config.get("repos", []):
            for hook in repo.get("hooks", []):
                all_hooks.append(hook.get("id", ""))

        # Check for ruff or python lint hooks
        has_python_lint = any("ruff" in h or "python" in h.lower() for h in all_hooks)
        assert has_python_lint, "No Python linting hook configured"


class TestGitHubWorkflowsExist:
    """Tests that GitHub Actions workflows exist."""

    def test_workflows_directory_exists(self, workflows_dir: Path):
        """Test that .github/workflows directory exists."""
        assert workflows_dir.exists(), f"Workflows directory not found: {workflows_dir}"

    def test_ci_workflow_exists(self, workflows_dir: Path):
        """Test that ci.yml workflow exists."""
        ci = workflows_dir / "ci.yml"
        assert ci.exists(), f"CI workflow not found: {ci}"

    def test_build_workflow_exists(self, workflows_dir: Path):
        """Test that build.yml workflow exists."""
        build = workflows_dir / "build.yml"
        assert build.exists(), f"Build workflow not found: {build}"

    def test_test_workflow_exists(self, workflows_dir: Path):
        """Test that test.yml workflow exists."""
        test = workflows_dir / "test.yml"
        assert test.exists(), f"Test workflow not found: {test}"

    def test_release_workflow_exists(self, workflows_dir: Path):
        """Test that release.yml workflow exists."""
        release = workflows_dir / "release.yml"
        assert release.exists(), f"Release workflow not found: {release}"


class TestCIWorkflowContent:
    """Tests for CI workflow content validity."""

    def test_ci_workflow_valid_yaml(self, workflows_dir: Path):
        """Test that ci.yml is valid YAML."""
        ci_path = workflows_dir / "ci.yml"
        if ci_path.exists():
            with open(ci_path) as f:
                try:
                    content = yaml.safe_load(f)
                    assert content is not None
                    assert "jobs" in content or "on" in content
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in ci.yml: {e}")

    def test_ci_has_python_job(self, workflows_dir: Path):
        """Test that CI has Python testing job."""
        ci_path = workflows_dir / "ci.yml"
        if ci_path.exists():
            with open(ci_path) as f:
                content = yaml.safe_load(f)
                jobs = content.get("jobs", {})
                python_jobs = [k for k in jobs if "python" in k.lower() or "test" in k.lower()]
                assert len(python_jobs) > 0, "No Python test job in CI"

    def test_ci_has_dotnet_job(self, workflows_dir: Path):
        """Test that CI has .NET build job."""
        ci_path = workflows_dir / "ci.yml"
        if ci_path.exists():
            with open(ci_path) as f:
                content = yaml.safe_load(f)
                jobs = content.get("jobs", {})
                dotnet_jobs = [
                    k
                    for k in jobs
                    if "dotnet" in k.lower() or "build" in k.lower() or "csharp" in k.lower()
                ]
                assert len(dotnet_jobs) > 0, "No .NET build job in CI"


class TestCIPipelineStages:
    """Tests for CI pipeline stage configuration."""

    def test_verify_script_exists(self, project_root: Path):
        """Test that verify.ps1 script exists."""
        script = project_root / "scripts" / "verify.ps1"
        assert script.exists(), f"Verify script not found: {script}"

    def test_verify_script_has_stages(self, project_root: Path):
        """Test that verify.ps1 defines multiple stages."""
        script = project_root / "scripts" / "verify.ps1"
        if script.exists():
            content = script.read_text(encoding="utf-8", errors="ignore")
            # Check for stage-related content
            assert "Stage" in content or "stage" in content, "No stages defined in verify.ps1"


class TestPreCommitScripts:
    """Tests that pre-commit hook scripts are valid Python."""

    def test_check_secrets_script_valid(self, project_root: Path):
        """Test that check_secrets.py has valid Python syntax."""
        script = project_root / "scripts" / "hooks" / "check_secrets.py"
        if script.exists():
            try:
                compile(script.read_text(), str(script), "exec")
            except SyntaxError as e:
                pytest.fail(f"Syntax error in check_secrets.py: {e}")

    def test_check_large_files_script_valid(self, project_root: Path):
        """Test that check_large_files.py has valid Python syntax."""
        script = project_root / "scripts" / "hooks" / "check_large_files.py"
        if script.exists():
            try:
                compile(script.read_text(), str(script), "exec")
            except SyntaxError as e:
                pytest.fail(f"Syntax error in check_large_files.py: {e}")

    def test_check_conflict_markers_script_valid(self, project_root: Path):
        """Test that check_conflict_markers.py has valid Python syntax."""
        script = project_root / "scripts" / "hooks" / "check_conflict_markers.py"
        if script.exists():
            try:
                compile(script.read_text(), str(script), "exec")
            except SyntaxError as e:
                pytest.fail(f"Syntax error in check_conflict_markers.py: {e}")


class TestCIArtifacts:
    """Tests for CI artifact configuration."""

    def test_codecov_configured(self, workflows_dir: Path):
        """Test that codecov is configured in CI."""
        ci_path = workflows_dir / "ci.yml"
        if ci_path.exists():
            content = ci_path.read_text()
            # Check for codecov action
            has_codecov = "codecov" in content.lower()
            # Either codecov or some coverage upload should exist
            has_coverage = has_codecov or "coverage" in content.lower()
            assert has_coverage, "No coverage reporting configured"

    def test_artifact_upload_configured(self, workflows_dir: Path):
        """Test that artifact upload is configured."""
        ci_path = workflows_dir / "ci.yml"
        if ci_path.exists():
            content = ci_path.read_text()
            assert "upload-artifact" in content, "No artifact upload configured"


class TestCITriggers:
    """Tests for CI trigger configuration."""

    def test_ci_triggers_on_push(self, workflows_dir: Path):
        """Test that CI triggers on push."""
        ci_path = workflows_dir / "ci.yml"
        if ci_path.exists():
            with open(ci_path) as f:
                content = yaml.safe_load(f)
                on_config = content.get("on", content.get(True, {}))
                # YAML parses 'on:' as True in some cases
                if on_config is None:
                    on_config = {}
                if isinstance(on_config, bool):
                    # Check raw file content
                    raw_content = ci_path.read_text()
                    has_push = "push:" in raw_content
                else:
                    has_push = "push" in on_config if isinstance(on_config, dict) else False
                assert has_push, "CI not triggered on push"

    def test_ci_triggers_on_pull_request(self, workflows_dir: Path):
        """Test that CI triggers on pull request."""
        ci_path = workflows_dir / "ci.yml"
        if ci_path.exists():
            with open(ci_path) as f:
                content = yaml.safe_load(f)
                on_config = content.get("on", content.get(True, {}))
                # YAML parses 'on:' as True in some cases
                if on_config is None:
                    on_config = {}
                if isinstance(on_config, bool):
                    # Check raw file content
                    raw_content = ci_path.read_text()
                    has_pr = "pull_request:" in raw_content
                else:
                    has_pr = "pull_request" in on_config if isinstance(on_config, dict) else False
                assert has_pr, "CI not triggered on pull request"
