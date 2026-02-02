"""
Tests for the Completion Evidence Guard.

Covers clean/dirty tree, staged/unstaged/untracked markers, guarded vs non-guarded paths,
code fence false positive handling, and git-unavailable behavior.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure project root on path (conftest does this; guard for direct run)
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from tools.overseer.verification import completion_guard as guard_module


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repo with initial commit."""
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    # Required for git to run in temp dir (no user identity in CI)
    subprocess.run(
        ["git", "config", "user.email", "test@test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    (tmp_path / "README").write_text("initial")
    subprocess.run(["git", "add", "README"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def test_clean_working_tree_passes(temp_git_repo: Path) -> None:
    """Empty git status returns PASS."""
    with patch.object(guard_module, "PROJECT_ROOT", temp_git_repo):
        passed, report = guard_module.run_guard()
    assert passed is True
    assert report.get("passed") is True
    assert report.get("dirty") is False


def test_dirty_tree_no_markers_passes(temp_git_repo: Path) -> None:
    """Modified files without completion markers PASS."""
    (temp_git_repo / "docs").mkdir(exist_ok=True)
    (temp_git_repo / "docs" / "tasks").mkdir(exist_ok=True)
    (temp_git_repo / "docs" / "tasks" / "foo.md").write_text("Hello world.\nNo [x] here.")
    with patch.object(guard_module, "PROJECT_ROOT", temp_git_repo):
        passed, report = guard_module.run_guard()
    assert passed is True
    assert report.get("passed") is True
    assert report.get("dirty") is True


def test_staged_completion_marker_fails(temp_git_repo: Path) -> None:
    """Staged diff with [x] in guarded path fails."""
    (temp_git_repo / "docs").mkdir(exist_ok=True)
    (temp_git_repo / "docs" / "tasks").mkdir(exist_ok=True)
    (temp_git_repo / "docs" / "tasks" / "task.md").write_text("- [x] Done\n")
    subprocess.run(["git", "add", "docs/tasks/task.md"], cwd=temp_git_repo, check=True, capture_output=True)
    with patch.object(guard_module, "PROJECT_ROOT", temp_git_repo):
        passed, report = guard_module.run_guard()
    assert passed is False
    assert report.get("passed") is False
    assert "hits" in report
    assert any(h["source"] == "staged" for h in report["hits"])


def test_unstaged_completion_marker_fails(temp_git_repo: Path) -> None:
    """Unstaged diff with status: complete fails."""
    (temp_git_repo / "docs").mkdir(exist_ok=True)
    (temp_git_repo / "docs" / "tasks").mkdir(exist_ok=True)
    (temp_git_repo / "docs" / "tasks" / "task.md").write_text("Initial line.\n")
    subprocess.run(["git", "add", "docs/tasks/task.md"], cwd=temp_git_repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "add task"], cwd=temp_git_repo, check=True, capture_output=True)
    (temp_git_repo / "docs" / "tasks" / "task.md").write_text("Initial line.\nstatus: complete\n")
    with patch.object(guard_module, "PROJECT_ROOT", temp_git_repo):
        passed, report = guard_module.run_guard()
    assert passed is False
    assert report.get("passed") is False
    assert any(h["source"] == "unstaged" for h in report.get("hits", []))


@pytest.mark.skipif(os.name == "nt", reason="Untracked path handling in temp git repo differs on Windows")
def test_untracked_marker_in_guarded_path_fails(temp_git_repo: Path) -> None:
    """New file in guarded path with markers fails."""
    (temp_git_repo / ".cursor").mkdir(exist_ok=True)
    (temp_git_repo / ".cursor" / "STATE.md").write_text("- [x] Item\n")
    with patch.object(guard_module, "PROJECT_ROOT", temp_git_repo):
        passed, report = guard_module.run_guard()
    assert passed is False, f"Expected FAIL for untracked guarded file with [x]; got {report}"
    assert report.get("passed") is False
    assert report.get("hits"), "Expected at least one hit for uncommitted completion marker in guarded path"


def test_untracked_marker_outside_guard_passes(temp_git_repo: Path) -> None:
    """New file in src/ with markers passes (not guarded)."""
    (temp_git_repo / "src").mkdir(exist_ok=True)
    (temp_git_repo / "src" / "readme.md").write_text("- [x] Done\n")
    with patch.object(guard_module, "PROJECT_ROOT", temp_git_repo):
        passed, report = guard_module.run_guard()
    assert passed is True
    assert report.get("passed") is True


def test_code_fence_false_positive_handled(temp_git_repo: Path) -> None:
    """Markdown code fence containing [x] as example does not trigger fail."""
    (temp_git_repo / "docs").mkdir(exist_ok=True)
    (temp_git_repo / "docs" / "tasks").mkdir(exist_ok=True)
    content = """# Task
Example checklist in code:
```
- [x] completed
- [ ] pending
```
Real content has no completion.
"""
    (temp_git_repo / "docs" / "tasks" / "fenced.md").write_text(content)
    with patch.object(guard_module, "PROJECT_ROOT", temp_git_repo):
        passed, report = guard_module.run_guard()
    assert passed is True, f"Expected PASS with code-fenced [x]; got {report}"


def test_git_unavailable_fails_gracefully() -> None:
    """Returns failure when git cannot be run."""
    with patch.object(guard_module, "_run_git", return_value=None):
        passed, report = guard_module.run_guard()
    assert passed is False
    assert report.get("passed") is False
    assert "git" in report.get("reason", "").lower()
