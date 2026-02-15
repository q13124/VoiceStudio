"""Tests for Overseer domain value objects."""

from datetime import datetime

import pytest

from tools.overseer.domain.value_objects import (
    CodeLocation,
    Fix,
    ResolutionLog,
    RootCause,
    RootCauseCategory,
    ValidationResult,
)


class TestCodeLocation:
    """Tests for CodeLocation value object."""

    def test_str_with_line_and_function(self):
        """String representation includes line and function."""
        loc = CodeLocation(
            file="backend/api/routes/voice.py",
            line=123,
            function="synthesize",
        )

        result = str(loc)
        assert "voice.py:123" in result
        assert "synthesize" in result

    def test_str_with_line_only(self):
        """String representation with line but no function."""
        loc = CodeLocation(file="test.py", line=45)
        result = str(loc)
        assert result == "test.py:45"

    def test_str_file_only(self):
        """String representation with file only."""
        loc = CodeLocation(file="test.py")
        result = str(loc)
        assert result == "test.py"


class TestRootCause:
    """Tests for RootCause value object."""

    def test_immutable(self):
        """RootCause is immutable (frozen dataclass)."""
        root_cause = RootCause(
            category=RootCauseCategory.CODE_LOGIC,
            location=CodeLocation(file="test.py"),
            description="Null pointer",
            evidence_paths=["log.txt"],
            confidence=0.9,
        )

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            root_cause.description = "Changed"

    def test_confidence_validation(self):
        """Confidence must be between 0.0 and 1.0."""
        with pytest.raises(ValueError, match="Confidence must be between"):
            RootCause(
                category=RootCauseCategory.CODE_LOGIC,
                location=CodeLocation(file="test.py"),
                description="Bug",
                evidence_paths=[],
                confidence=1.5,  # Invalid
            )


class TestResolutionLog:
    """Tests for ResolutionLog value object."""

    def test_to_markdown_includes_all_sections(self):
        """Markdown output includes all 6 required sections."""
        validation = ValidationResult(
            passed=True,
            build_success=True,
            tests_passed=10,
            tests_failed=0,
            gate_status="GREEN",
            errors=[],
            proof_artifacts=["proof.json"],
            executed_at=datetime.now(),
        )

        log = ResolutionLog(
            issue_id="ISS-001",
            resolved_at=datetime.now(),
            resolved_by="debug-agent",
            root_cause="Null pointer in route handler",
            fix_rationale="Added null check and validation",
            discovery_process="Traced logs with correlation ID",
            originator_analysis="Introduced in TASK-0010",
            prevention_recommendations=["Add integration test", "Add validation layer"],
            validation_results=validation,
            proof_artifacts=["proof.json", "test_results.xml"],
        )

        markdown = log.to_markdown()

        # Check all required sections present
        assert "# Resolution Summary: ISS-001" in markdown
        assert "## 1. Cause of Bug" in markdown
        assert "## 2. Why Fix Works" in markdown
        assert "## 3. Discovery Process" in markdown
        assert "## 4. Originator Analysis" in markdown
        assert "## 5. Prevention Recommendations" in markdown
        assert "## 6. Validation Results" in markdown

        # Check content
        assert "Null pointer in route handler" in markdown
        assert "Added null check" in markdown
        assert "Add integration test" in markdown
        assert "proof.json" in markdown

    def test_immutable(self):
        """ResolutionLog is immutable."""
        log = ResolutionLog(
            issue_id="ISS-001",
            resolved_at=datetime.now(),
            resolved_by="test",
            root_cause="cause",
            fix_rationale="rationale",
            discovery_process="process",
            originator_analysis="origin",
            prevention_recommendations=[],
            validation_results=ValidationResult(True, True, 0, 0, "GREEN", [], [], datetime.now()),
            proof_artifacts=[],
        )

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            log.issue_id = "ISS-002"


class TestValidationResult:
    """Tests for ValidationResult value object."""

    def test_is_valid_requires_all_pass(self):
        """is_valid is True only if passed, build success, and no test failures."""
        # All pass
        result = ValidationResult(
            passed=True,
            build_success=True,
            tests_passed=10,
            tests_failed=0,
            gate_status="GREEN",
            errors=[],
            proof_artifacts=[],
            executed_at=datetime.now(),
        )
        assert result.is_valid

        # Build failed
        result = ValidationResult(
            passed=True,
            build_success=False,
            tests_passed=10,
            tests_failed=0,
            gate_status="GREEN",
            errors=[],
            proof_artifacts=[],
            executed_at=datetime.now(),
        )
        assert not result.is_valid

        # Tests failed
        result = ValidationResult(
            passed=True,
            build_success=True,
            tests_passed=8,
            tests_failed=2,
            gate_status="GREEN",
            errors=[],
            proof_artifacts=[],
            executed_at=datetime.now(),
        )
        assert not result.is_valid


class TestFix:
    """Tests for Fix value object."""

    def test_immutable(self):
        """Fix is immutable."""
        fix = Fix(
            issue_id="ISS-001",
            file_changes=[],
            rationale="Test fix",
            estimated_risk="low",
        )

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            fix.issue_id = "ISS-002"
