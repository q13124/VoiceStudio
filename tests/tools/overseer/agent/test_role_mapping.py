"""Tests for VoiceStudio role id to AgentRole mapping."""

from __future__ import annotations

import pytest

from tools.overseer.agent.identity import AgentRole
from tools.overseer.agent.role_mapping import (
    VoiceStudioRoleId,
    agent_role_to_role_id,
    role_to_agent_role,
)


class TestRoleToAgentRole:
    def test_numeric_zero(self) -> None:
        assert role_to_agent_role(0) == AgentRole.OVERSEER

    def test_numeric_one_through_six(self) -> None:
        assert role_to_agent_role(1) == AgentRole.REVIEWER
        assert role_to_agent_role(2) == AgentRole.BUILDER
        assert role_to_agent_role(3) == AgentRole.CODER
        assert role_to_agent_role(4) == AgentRole.CODER
        assert role_to_agent_role(5) == AgentRole.CODER
        assert role_to_agent_role(6) == AgentRole.BUILDER

    def test_string_digit_ids(self) -> None:
        assert role_to_agent_role("0") == AgentRole.OVERSEER
        assert role_to_agent_role("1") == AgentRole.REVIEWER
        assert role_to_agent_role("6") == AgentRole.BUILDER

    def test_short_names(self) -> None:
        assert role_to_agent_role("overseer") == AgentRole.OVERSEER
        assert role_to_agent_role("system-architect") == AgentRole.REVIEWER
        assert role_to_agent_role("build-tooling") == AgentRole.BUILDER
        assert role_to_agent_role("ui-engineer") == AgentRole.CODER
        assert role_to_agent_role("core-platform") == AgentRole.CODER
        assert role_to_agent_role("engine-engineer") == AgentRole.CODER
        assert role_to_agent_role("release-engineer") == AgentRole.BUILDER
        assert role_to_agent_role("validator") == AgentRole.REVIEWER
        assert role_to_agent_role("skeptical_validator") == AgentRole.REVIEWER

    def test_unknown_defaults_to_coder(self) -> None:
        assert role_to_agent_role("unknown-role") == AgentRole.CODER
        assert role_to_agent_role(99) == AgentRole.CODER

    def test_none_defaults_to_coder(self) -> None:
        assert role_to_agent_role(None) == AgentRole.CODER  # type: ignore[arg-type]


class TestAgentRoleToRoleId:
    def test_overseer_maps_to_zero_and_overseer(self) -> None:
        ids = agent_role_to_role_id(AgentRole.OVERSEER)
        assert 0 in ids
        assert "overseer" in ids

    def test_reviewer_maps_to_one_architect_validator(self) -> None:
        ids = agent_role_to_role_id(AgentRole.REVIEWER)
        assert 1 in ids
        assert "system-architect" in ids
        assert "validator" in ids

    def test_builder_maps_to_two_and_six(self) -> None:
        ids = agent_role_to_role_id(AgentRole.BUILDER)
        assert 2 in ids
        assert 6 in ids
        assert "build-tooling" in ids
        assert "release-engineer" in ids

    def test_coder_maps_to_three_four_five(self) -> None:
        ids = agent_role_to_role_id(AgentRole.CODER)
        assert 3 in ids
        assert 4 in ids
        assert 5 in ids
        assert "ui-engineer" in ids
        assert "core-platform" in ids
        assert "engine-engineer" in ids
