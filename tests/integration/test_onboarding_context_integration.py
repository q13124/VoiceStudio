"""
Integration tests for onboarding + context bundle flow.

These tests verify that:
1. OnboardingAssembler correctly integrates with ContextManager
2. Context bundles are allocated during onboarding
3. Packets are rendered with context bundle content
4. Role-specific context is properly filtered
5. Graceful degradation when components are unavailable

Phase 2 Context Management Automation - Integration Tests
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Test fixtures and mocks
# ---------------------------------------------------------------------------


@dataclass
class MockContextBundle:
    """Mock context bundle for testing."""

    role: str
    task_id: str | None
    sources: dict[str, str]

    def to_preamble_markdown(self) -> str:
        """Render mock preamble."""
        lines = [
            "## Context Bundle",
            "",
            f"**Role**: {self.role}",
            f"**Task**: {self.task_id or 'None'}",
            "",
            "### Sources",
            "",
        ]
        for name, content in self.sources.items():
            lines.append(f"- **{name}**: {content[:50]}...")
        return "\n".join(lines)

    def to_part_markdown(self) -> str:
        """Render P.A.R.T. structure."""
        return self.to_preamble_markdown()


class MockContextManager:
    """Mock ContextManager for testing onboarding integration."""

    def __init__(
        self,
        should_fail: bool = False,
        custom_bundle: MockContextBundle | None = None,
    ):
        self._should_fail = should_fail
        self._custom_bundle = custom_bundle
        self._allocations: list[dict[str, Any]] = []

    def allocate(self, context) -> MockContextBundle:
        """Mock allocation that tracks calls."""
        if self._should_fail:
            raise RuntimeError("Context allocation failed")

        self._allocations.append({
            "task_id": getattr(context, "task_id", None),
            "phase": getattr(context, "phase", None),
            "role": getattr(context, "role", None),
        })

        if self._custom_bundle:
            return self._custom_bundle

        return MockContextBundle(
            role=getattr(context, "role", "unknown"),
            task_id=getattr(context, "task_id", None),
            sources={
                "state": "Current phase: Construct",
                "task": f"Task {getattr(context, 'task_id', 'N/A')}",
                "ledger": "No blockers",
            },
        )

    @property
    def allocations(self) -> list[dict[str, Any]]:
        """Return tracked allocations for assertions."""
        return self._allocations


@pytest.fixture
def temp_state_file(tmp_path: Path):
    """Create temporary STATE.md for testing."""
    state_content = """# VoiceStudio Session State

## Current Phase
Construct

## Active Task
TASK-0042 - Test Context Integration

## Blockers
- None

## Next 3 Steps
1. Complete integration tests
2. Verify all components
3. Update documentation
"""
    state_file = tmp_path / ".cursor" / "STATE.md"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(state_content, encoding="utf-8")
    return state_file


@pytest.fixture
def mock_role_registry():
    """Create mock role registry."""
    mock = MagicMock()

    mock_role = MagicMock()
    mock_role.id = "4"
    mock_role.short_name = "core-platform"
    mock_role.name = "Core Platform Engineer"
    mock_role.prompt_path = ".cursor/prompts/ROLE_4_CORE_PLATFORM_PROMPT.md"
    mock_role.guide_path = "docs/governance/roles/ROLE_4_CORE_PLATFORM_GUIDE.md"
    mock_role.primary_gates = ["D", "E"]

    mock.get_role.return_value = mock_role
    return mock


# ---------------------------------------------------------------------------
# Integration Tests: Onboarding + Context Bundle
# ---------------------------------------------------------------------------


class TestOnboardingContextIntegration:
    """Integration tests for onboarding with context manager."""

    def test_assembler_uses_context_manager(self) -> None:
        """OnboardingAssembler should use injected ContextManager."""
        mock_cm = MockContextManager()

        with patch("tools.onboarding.core.assembler.RoleRegistry") as mock_registry_cls:
            mock_registry = MagicMock()
            mock_role = MagicMock()
            mock_role.id = "4"
            mock_role.short_name = "core-platform"
            mock_role.name = "Core Platform Engineer"
            mock_role.prompt_path = ".cursor/prompts/ROLE_4_CORE_PLATFORM_PROMPT.md"
            mock_role.guide_path = "docs/governance/roles/ROLE_4_CORE_PLATFORM_GUIDE.md"
            mock_role.primary_gates = ["D", "E"]
            mock_registry.get_role.return_value = mock_role
            mock_registry_cls.from_config.return_value = mock_registry

            with patch("tools.onboarding.core.assembler.PromptSource") as mock_ps:
                mock_prompt = MagicMock()
                mock_prompt.identity_section = "Role Identity"
                mock_prompt.next_actions = "Next actions"
                mock_prompt.full_text = "Full prompt text"
                mock_ps.return_value.load.return_value = mock_prompt

                with patch("tools.onboarding.core.assembler.GuideSource") as mock_gs:
                    mock_guide = MagicMock()
                    mock_guide.summary = "Guide summary"
                    mock_guide.full_text = ""
                    mock_gs.return_value.summarize.return_value = mock_guide

                    with patch("tools.onboarding.core.assembler.StateSource") as mock_ss:
                        mock_state = MagicMock()
                        mock_state.phase = "Construct"
                        mock_state.active_gate = "D"
                        mock_state.active_task_id = "TASK-0042"
                        mock_state.active_task_title = "Test task"

                        mock_task = MagicMock()
                        mock_task.id = "TASK-0042"

                        mock_ss.return_value.load.return_value = (mock_state, mock_task)

                        with patch("tools.onboarding.core.assembler.RoleContextSource") as mock_cs:
                            mock_context = MagicMock()
                            mock_context.blockers = []
                            mock_cs.return_value.load.return_value = mock_context

                            from tools.onboarding.core.assembler import OnboardingAssembler

                            assembler = OnboardingAssembler(
                                context_manager=mock_cm
                            )
                            packet = assembler.assemble("4")

                            # Verify context manager was called
                            assert len(mock_cm.allocations) == 1
                            assert mock_cm.allocations[0]["role"] == "core-platform"
                            assert mock_cm.allocations[0]["task_id"] == "TASK-0042"

                            # Verify packet has context bundle
                            assert packet.context_bundle is not None
                            assert packet.context_bundle.role == "core-platform"

    def test_context_bundle_in_rendered_output(self) -> None:
        """Context bundle should appear in rendered packet."""
        mock_bundle = MockContextBundle(
            role="core-platform",
            task_id="TASK-0042",
            sources={
                "state": "Phase: Construct, Task: TASK-0042",
                "ledger": "No blockers for Gate D",
            },
        )
        mock_cm = MockContextManager(custom_bundle=mock_bundle)

        with patch("tools.onboarding.core.assembler.RoleRegistry") as mock_registry_cls:
            mock_registry = MagicMock()
            mock_role = MagicMock()
            mock_role.id = "4"
            mock_role.short_name = "core-platform"
            mock_role.name = "Core Platform Engineer"
            mock_role.prompt_path = ".cursor/prompts/ROLE_4_CORE_PLATFORM_PROMPT.md"
            mock_role.guide_path = "docs/governance/roles/ROLE_4_CORE_PLATFORM_GUIDE.md"
            mock_role.primary_gates = ["D", "E"]
            mock_registry.get_role.return_value = mock_role
            mock_registry_cls.from_config.return_value = mock_registry

            with patch("tools.onboarding.core.assembler.PromptSource") as mock_ps:
                mock_prompt = MagicMock()
                mock_prompt.identity_section = "Role Identity"
                mock_prompt.next_actions = "Next actions"
                mock_prompt.full_text = "Full prompt text"
                mock_ps.return_value.load.return_value = mock_prompt

                with patch("tools.onboarding.core.assembler.GuideSource") as mock_gs:
                    mock_guide = MagicMock()
                    mock_guide.summary = "Guide summary"
                    mock_guide.full_text = ""
                    mock_gs.return_value.summarize.return_value = mock_guide

                    with patch("tools.onboarding.core.assembler.StateSource") as mock_ss:
                        mock_state = MagicMock()
                        mock_state.phase = "Construct"
                        mock_state.active_gate = "D"
                        mock_state.active_task_id = "TASK-0042"
                        mock_state.active_task_title = "Test task"

                        mock_task = MagicMock()
                        mock_task.id = "TASK-0042"

                        mock_ss.return_value.load.return_value = (mock_state, mock_task)

                        with patch("tools.onboarding.core.assembler.RoleContextSource") as mock_cs:
                            mock_context = MagicMock()
                            mock_context.blockers = []
                            mock_cs.return_value.load.return_value = mock_context

                            from tools.onboarding.core.assembler import OnboardingAssembler

                            assembler = OnboardingAssembler(
                                context_manager=mock_cm
                            )
                            packet = assembler.assemble("4")
                            rendered = assembler.render(packet)

                            # Context bundle content should be in output
                            assert "Context Bundle" in rendered
                            assert "core-platform" in rendered
                            assert "TASK-0042" in rendered

    def test_graceful_degradation_when_context_manager_fails(self) -> None:
        """Onboarding should succeed even if ContextManager fails."""
        mock_cm = MockContextManager(should_fail=True)

        with patch("tools.onboarding.core.assembler.RoleRegistry") as mock_registry_cls:
            mock_registry = MagicMock()
            mock_role = MagicMock()
            mock_role.id = "4"
            mock_role.short_name = "core-platform"
            mock_role.name = "Core Platform Engineer"
            mock_role.prompt_path = ".cursor/prompts/ROLE_4_CORE_PLATFORM_PROMPT.md"
            mock_role.guide_path = "docs/governance/roles/ROLE_4_CORE_PLATFORM_GUIDE.md"
            mock_role.primary_gates = ["D", "E"]
            mock_registry.get_role.return_value = mock_role
            mock_registry_cls.from_config.return_value = mock_registry

            with patch("tools.onboarding.core.assembler.PromptSource") as mock_ps:
                mock_prompt = MagicMock()
                mock_prompt.identity_section = "Role Identity"
                mock_prompt.next_actions = "Next actions"
                mock_prompt.full_text = "Full prompt text"
                mock_ps.return_value.load.return_value = mock_prompt

                with patch("tools.onboarding.core.assembler.GuideSource") as mock_gs:
                    mock_guide = MagicMock()
                    mock_guide.summary = "Guide summary"
                    mock_guide.full_text = ""
                    mock_gs.return_value.summarize.return_value = mock_guide

                    with patch("tools.onboarding.core.assembler.StateSource") as mock_ss:
                        mock_state = MagicMock()
                        mock_state.phase = "Construct"
                        mock_state.active_gate = "D"
                        mock_state.active_task_id = "TASK-0042"
                        mock_state.active_task_title = "Test task"

                        mock_task = MagicMock()
                        mock_task.id = "TASK-0042"

                        mock_ss.return_value.load.return_value = (mock_state, mock_task)

                        with patch("tools.onboarding.core.assembler.RoleContextSource") as mock_cs:
                            mock_context = MagicMock()
                            mock_context.blockers = []
                            mock_cs.return_value.load.return_value = mock_context

                            from tools.onboarding.core.assembler import OnboardingAssembler

                            assembler = OnboardingAssembler(
                                context_manager=mock_cm
                            )

                            # Should not raise - graceful degradation
                            packet = assembler.assemble("4")

                            # Packet should still be valid, just without bundle
                            assert packet.role.short_name == "core-platform"
                            assert packet.context_bundle is None

    def test_no_context_manager_produces_valid_packet(self) -> None:
        """Onboarding without ContextManager should produce valid packet."""
        with patch("tools.onboarding.core.assembler.RoleRegistry") as mock_registry_cls:
            mock_registry = MagicMock()
            mock_role = MagicMock()
            mock_role.id = "4"
            mock_role.short_name = "core-platform"
            mock_role.name = "Core Platform Engineer"
            mock_role.prompt_path = ".cursor/prompts/ROLE_4_CORE_PLATFORM_PROMPT.md"
            mock_role.guide_path = "docs/governance/roles/ROLE_4_CORE_PLATFORM_GUIDE.md"
            mock_role.primary_gates = ["D", "E"]
            mock_registry.get_role.return_value = mock_role
            mock_registry_cls.from_config.return_value = mock_registry

            with patch("tools.onboarding.core.assembler.PromptSource") as mock_ps:
                mock_prompt = MagicMock()
                mock_prompt.identity_section = "Role Identity"
                mock_prompt.next_actions = "Next actions"
                mock_prompt.full_text = "Full prompt text"
                mock_ps.return_value.load.return_value = mock_prompt

                with patch("tools.onboarding.core.assembler.GuideSource") as mock_gs:
                    mock_guide = MagicMock()
                    mock_guide.summary = "Guide summary"
                    mock_guide.full_text = ""
                    mock_gs.return_value.summarize.return_value = mock_guide

                    with patch("tools.onboarding.core.assembler.StateSource") as mock_ss:
                        mock_state = MagicMock()
                        mock_state.phase = "Construct"
                        mock_state.active_gate = "D"
                        mock_state.active_task_id = None
                        mock_state.active_task_title = None

                        mock_ss.return_value.load.return_value = (mock_state, None)

                        with patch("tools.onboarding.core.assembler.RoleContextSource") as mock_cs:
                            mock_context = MagicMock()
                            mock_context.blockers = []
                            mock_cs.return_value.load.return_value = mock_context

                            with patch("tools.onboarding.core.assembler._default_context_manager") as mock_dcm:
                                mock_dcm.return_value = None

                                from tools.onboarding.core.assembler import OnboardingAssembler

                                assembler = OnboardingAssembler(
                                    context_manager=None
                                )
                                packet = assembler.assemble("4")

                                # Packet should be valid
                                assert packet.role is not None
                                assert packet.prompt is not None
                                assert packet.guide is not None
                                assert packet.project_state is not None
                                assert packet.context_bundle is None


class TestContextAllocationParameters:
    """Tests for context allocation parameter passing."""

    def test_task_id_passed_to_context_manager(self) -> None:
        """Task ID from state should be passed to context allocation."""
        mock_cm = MockContextManager()

        with patch("tools.onboarding.core.assembler.RoleRegistry") as mock_registry_cls:
            mock_registry = MagicMock()
            mock_role = MagicMock()
            mock_role.id = "4"
            mock_role.short_name = "core-platform"
            mock_role.name = "Core Platform Engineer"
            mock_role.prompt_path = ".cursor/prompts/ROLE_4_CORE_PLATFORM_PROMPT.md"
            mock_role.guide_path = None
            mock_role.primary_gates = []
            mock_registry.get_role.return_value = mock_role
            mock_registry_cls.from_config.return_value = mock_registry

            with patch("tools.onboarding.core.assembler.PromptSource") as mock_ps:
                mock_prompt = MagicMock()
                mock_prompt.identity_section = ""
                mock_prompt.next_actions = ""
                mock_prompt.full_text = ""
                mock_ps.return_value.load.return_value = mock_prompt

                with patch("tools.onboarding.core.assembler.GuideSource") as mock_gs:
                    mock_guide = MagicMock()
                    mock_guide.summary = ""
                    mock_guide.full_text = ""
                    mock_gs.return_value.summarize.return_value = mock_guide

                    with patch("tools.onboarding.core.assembler.StateSource") as mock_ss:
                        mock_state = MagicMock()
                        mock_state.phase = "Construct"
                        mock_state.active_gate = "D"
                        mock_state.active_task_id = "TASK-0099"
                        mock_state.active_task_title = "Specific task"

                        mock_task = MagicMock()
                        mock_task.id = "TASK-0099"

                        mock_ss.return_value.load.return_value = (mock_state, mock_task)

                        with patch("tools.onboarding.core.assembler.RoleContextSource") as mock_cs:
                            mock_context = MagicMock()
                            mock_context.blockers = []
                            mock_cs.return_value.load.return_value = mock_context

                            from tools.onboarding.core.assembler import OnboardingAssembler

                            assembler = OnboardingAssembler(
                                context_manager=mock_cm
                            )
                            assembler.assemble("4")

                            assert mock_cm.allocations[0]["task_id"] == "TASK-0099"

    def test_phase_passed_to_context_manager(self) -> None:
        """Phase from state should be passed to context allocation."""
        mock_cm = MockContextManager()

        with patch("tools.onboarding.core.assembler.RoleRegistry") as mock_registry_cls:
            mock_registry = MagicMock()
            mock_role = MagicMock()
            mock_role.id = "5"
            mock_role.short_name = "engine-engineer"
            mock_role.name = "Engine Engineer"
            mock_role.prompt_path = ".cursor/prompts/ROLE_5_ENGINE_ENGINEER_PROMPT.md"
            mock_role.guide_path = None
            mock_role.primary_gates = []
            mock_registry.get_role.return_value = mock_role
            mock_registry_cls.from_config.return_value = mock_registry

            with patch("tools.onboarding.core.assembler.PromptSource") as mock_ps:
                mock_prompt = MagicMock()
                mock_prompt.identity_section = ""
                mock_prompt.next_actions = ""
                mock_prompt.full_text = ""
                mock_ps.return_value.load.return_value = mock_prompt

                with patch("tools.onboarding.core.assembler.GuideSource") as mock_gs:
                    mock_guide = MagicMock()
                    mock_guide.summary = ""
                    mock_guide.full_text = ""
                    mock_gs.return_value.summarize.return_value = mock_guide

                    with patch("tools.onboarding.core.assembler.StateSource") as mock_ss:
                        mock_state = MagicMock()
                        mock_state.phase = "Verify"
                        mock_state.active_gate = "F"
                        mock_state.active_task_id = None
                        mock_state.active_task_title = None

                        mock_ss.return_value.load.return_value = (mock_state, None)

                        with patch("tools.onboarding.core.assembler.RoleContextSource") as mock_cs:
                            mock_context = MagicMock()
                            mock_context.blockers = []
                            mock_cs.return_value.load.return_value = mock_context

                            from tools.onboarding.core.assembler import OnboardingAssembler

                            assembler = OnboardingAssembler(
                                context_manager=mock_cm
                            )
                            assembler.assemble("5")

                            assert mock_cm.allocations[0]["phase"] == "Verify"
                            assert mock_cm.allocations[0]["role"] == "engine-engineer"


class TestPacketValidation:
    """Tests for packet component validation."""

    def test_validation_detects_missing_prompt(self) -> None:
        """Validation should detect missing prompt content."""
        from tools.onboarding.core.assembler import OnboardingAssembler
        from tools.onboarding.core.models import (
            GuideContent,
            ProjectState,
            PromptContent,
            RoleConfig,
        )

        with patch("tools.onboarding.core.assembler.RoleRegistry"):
            assembler = OnboardingAssembler.__new__(OnboardingAssembler)

            role = RoleConfig(
                id="4",
                short_name="core-platform",
                name="Core Platform",
                prompt_path="path",
            )

            # Empty prompt
            prompt = PromptContent(
                identity_section="",
                next_actions="",
                full_text="",  # Empty!
            )

            guide = GuideContent(summary="Summary", full_text="")
            state = ProjectState(phase="Construct")

            errors = assembler._validate_packet_components(role, prompt, guide, state)

            assert len(errors) > 0
            assert any("Prompt missing" in e for e in errors)

    def test_validation_passes_with_complete_components(self) -> None:
        """Validation should pass with all required components."""
        from tools.onboarding.core.assembler import OnboardingAssembler
        from tools.onboarding.core.models import (
            GuideContent,
            ProjectState,
            PromptContent,
            RoleConfig,
        )

        with patch("tools.onboarding.core.assembler.RoleRegistry"):
            assembler = OnboardingAssembler.__new__(OnboardingAssembler)

            role = RoleConfig(
                id="4",
                short_name="core-platform",
                name="Core Platform",
                prompt_path="path",
            )

            prompt = PromptContent(
                identity_section="Identity",
                next_actions="Actions",
                full_text="Full prompt content",
            )

            guide = GuideContent(summary="Summary", full_text="")
            state = ProjectState(phase="Construct")

            errors = assembler._validate_packet_components(role, prompt, guide, state)

            assert len(errors) == 0


class TestRoleSpecificContext:
    """Tests for role-specific context filtering."""

    def test_different_roles_get_different_context(self) -> None:
        """Different roles should receive appropriately filtered context."""
        mock_cm = MockContextManager()

        roles_tested = []

        for role_id, short_name in [("3", "ui-engineer"), ("4", "core-platform"), ("5", "engine-engineer")]:
            with patch("tools.onboarding.core.assembler.RoleRegistry") as mock_registry_cls:
                mock_registry = MagicMock()
                mock_role = MagicMock()
                mock_role.id = role_id
                mock_role.short_name = short_name
                mock_role.name = f"Role {role_id}"
                mock_role.prompt_path = f".cursor/prompts/ROLE_{role_id}_PROMPT.md"
                mock_role.guide_path = None
                mock_role.primary_gates = []
                mock_registry.get_role.return_value = mock_role
                mock_registry_cls.from_config.return_value = mock_registry

                with patch("tools.onboarding.core.assembler.PromptSource") as mock_ps:
                    mock_prompt = MagicMock()
                    mock_prompt.identity_section = ""
                    mock_prompt.next_actions = ""
                    mock_prompt.full_text = ""
                    mock_ps.return_value.load.return_value = mock_prompt

                    with patch("tools.onboarding.core.assembler.GuideSource") as mock_gs:
                        mock_guide = MagicMock()
                        mock_guide.summary = ""
                        mock_guide.full_text = ""
                        mock_gs.return_value.summarize.return_value = mock_guide

                        with patch("tools.onboarding.core.assembler.StateSource") as mock_ss:
                            mock_state = MagicMock()
                            mock_state.phase = "Construct"
                            mock_state.active_gate = "D"
                            mock_state.active_task_id = None
                            mock_state.active_task_title = None
                            mock_ss.return_value.load.return_value = (mock_state, None)

                            with patch("tools.onboarding.core.assembler.RoleContextSource") as mock_cs:
                                mock_context = MagicMock()
                                mock_context.blockers = []
                                mock_cs.return_value.load.return_value = mock_context

                                from tools.onboarding.core.assembler import OnboardingAssembler

                                assembler = OnboardingAssembler(
                                    context_manager=mock_cm
                                )
                                assembler.assemble(role_id)
                                roles_tested.append(short_name)

        # Verify all roles were allocated different context
        assert len(mock_cm.allocations) == 3
        allocated_roles = [a["role"] for a in mock_cm.allocations]
        assert "ui-engineer" in allocated_roles
        assert "core-platform" in allocated_roles
        assert "engine-engineer" in allocated_roles


# ---------------------------------------------------------------------------
# Integration Tests: End-to-End Flow
# ---------------------------------------------------------------------------


class TestEndToEndOnboardingFlow:
    """End-to-end tests for the complete onboarding flow."""

    def test_full_onboarding_cycle(self) -> None:
        """Test complete onboarding cycle: assemble -> validate -> render."""
        mock_cm = MockContextManager()

        with patch("tools.onboarding.core.assembler.RoleRegistry") as mock_registry_cls:
            mock_registry = MagicMock()
            mock_role = MagicMock()
            mock_role.id = "4"
            mock_role.short_name = "core-platform"
            mock_role.name = "Core Platform Engineer"
            mock_role.prompt_path = ".cursor/prompts/ROLE_4_CORE_PLATFORM_PROMPT.md"
            mock_role.guide_path = "docs/governance/roles/ROLE_4_CORE_PLATFORM_GUIDE.md"
            mock_role.primary_gates = ["D", "E"]
            mock_registry.get_role.return_value = mock_role
            mock_registry_cls.from_config.return_value = mock_registry

            with patch("tools.onboarding.core.assembler.PromptSource") as mock_ps:
                mock_prompt = MagicMock()
                mock_prompt.identity_section = "You are the Core Platform Engineer."
                mock_prompt.next_actions = "1. Check job state store\n2. Verify preflight"
                mock_prompt.full_text = "Full system prompt content..."
                mock_ps.return_value.load.return_value = mock_prompt

                with patch("tools.onboarding.core.assembler.GuideSource") as mock_gs:
                    mock_guide = MagicMock()
                    mock_guide.summary = "Responsible for storage durability and preflight."
                    mock_guide.full_text = ""
                    mock_gs.return_value.summarize.return_value = mock_guide

                    with patch("tools.onboarding.core.assembler.StateSource") as mock_ss:
                        mock_state = MagicMock()
                        mock_state.phase = "Construct"
                        mock_state.active_gate = "D"
                        mock_state.active_task_id = "TASK-0042"
                        mock_state.active_task_title = "Context Integration"

                        mock_task = MagicMock()
                        mock_task.id = "TASK-0042"

                        mock_ss.return_value.load.return_value = (mock_state, mock_task)

                        with patch("tools.onboarding.core.assembler.RoleContextSource") as mock_cs:
                            mock_context = MagicMock()
                            mock_context.blockers = []
                            mock_cs.return_value.load.return_value = mock_context

                            from tools.onboarding.core.assembler import OnboardingAssembler

                            # 1. Create assembler with context manager
                            assembler = OnboardingAssembler(
                                context_manager=mock_cm
                            )

                            # 2. Assemble packet
                            packet = assembler.assemble("4")

                            # 3. Validate packet components
                            assert packet.role.short_name == "core-platform"
                            assert packet.prompt.identity_section is not None
                            assert packet.guide.summary is not None
                            assert packet.project_state.phase == "Construct"
                            assert packet.context_bundle is not None

                            # 4. Render packet
                            rendered = assembler.render(packet)

                            # 5. Verify rendered output
                            assert "Core Platform Engineer" in rendered
                            assert "Construct" in rendered
                            assert "TASK-0042" in rendered
                            assert "Context Bundle" in rendered
