"""
VoiceStudio Role Id to AgentRole mapping.

Maps VoiceStudio roles (0-6, skeptical_validator / validator) to the
Agent Governance AgentRole enum so PolicyEngine can enforce policies per
VoiceStudio role. VoiceStudio roles are the source of truth; AgentRole
is used only for policy execution.

See ADR-015 (Architecture Integration Contract) and
docs/reports/verification/ARCHITECTURE_INTEGRATION_REVIEW_2026-01-28.md.
"""

from __future__ import annotations

from typing import Union

from .identity import AgentRole

# 0-6 or short_name from tools/onboarding/config/roles.json
VoiceStudioRoleId = Union[int, str]

# VoiceStudio role id -> AgentRole (0->OVERSEER, 1->REVIEWER, 2->BUILDER, 3/4/5->CODER, 6->BUILDER, 7->DEBUGGER; validator->REVIEWER)
_ROLE_TO_AGENT: dict[VoiceStudioRoleId, AgentRole] = {
    0: AgentRole.OVERSEER,
    1: AgentRole.REVIEWER,
    2: AgentRole.BUILDER,
    3: AgentRole.CODER,
    4: AgentRole.CODER,
    5: AgentRole.CODER,
    6: AgentRole.BUILDER,
    7: AgentRole.DEBUGGER,
    "0": AgentRole.OVERSEER,
    "1": AgentRole.REVIEWER,
    "2": AgentRole.BUILDER,
    "3": AgentRole.CODER,
    "4": AgentRole.CODER,
    "5": AgentRole.CODER,
    "6": AgentRole.BUILDER,
    "7": AgentRole.DEBUGGER,
    "overseer": AgentRole.OVERSEER,
    "system-architect": AgentRole.REVIEWER,
    "build-tooling": AgentRole.BUILDER,
    "ui-engineer": AgentRole.CODER,
    "core-platform": AgentRole.CODER,
    "engine-engineer": AgentRole.CODER,
    "release-engineer": AgentRole.BUILDER,
    "debug-agent": AgentRole.DEBUGGER,
    "debug": AgentRole.DEBUGGER,
    "debugger": AgentRole.DEBUGGER,
    "validator": AgentRole.REVIEWER,
    "skeptical_validator": AgentRole.REVIEWER,
    "skeptical-validator": AgentRole.REVIEWER,
}


def role_to_agent_role(role_id: VoiceStudioRoleId) -> AgentRole:
    """
    Map a VoiceStudio role id to AgentRole for policy execution.

    Args:
        role_id: 0-6, or short_name from roles.json (e.g. "overseer", "validator").

    Returns:
        The corresponding AgentRole. Unknown ids default to CODER to avoid
        over-restrictive denials.

    Raises:
        ValueError: If role_id is None or otherwise invalid (optional strict mode).
    """
    if role_id is None:
        return AgentRole.CODER
    key: VoiceStudioRoleId = int(role_id) if isinstance(role_id, str) and role_id.isdigit() else role_id
    return _ROLE_TO_AGENT.get(key, AgentRole.CODER)


def agent_role_to_role_id(ar: AgentRole) -> list[VoiceStudioRoleId]:
    """
    Reverse lookup: all VoiceStudio role ids that map to this AgentRole.

    Args:
        ar: An AgentRole.

    Returns:
        List of VoiceStudio role ids (int or str) that map to ar.
    """
    return [rid for rid, r in _ROLE_TO_AGENT.items() if r == ar]
