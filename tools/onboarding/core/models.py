from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RoleConfig:
    id: str
    short_name: str
    name: str
    prompt_path: str
    guide_path: str | None = None
    primary_gates: list[str] = field(default_factory=list)


@dataclass
class PromptContent:
    identity_section: str
    next_actions: str
    full_text: str


@dataclass
class GuideContent:
    summary: str
    full_text: str


@dataclass
class ProjectState:
    phase: str | None = None
    active_gate: str | None = None
    active_task_id: str | None = None
    active_task_title: str | None = None


@dataclass
class ActiveTask:
    id: str | None = None
    title: str | None = None
    priority: str | None = None
    blockers: str | None = None


@dataclass
class Blocker:
    id: str
    severity: str
    gate: str
    title: str
    owner_role: str


@dataclass
class RoleContext:
    blockers: list[Blocker] = field(default_factory=list)


@dataclass
class OnboardingPacket:
    role: RoleConfig
    prompt: PromptContent
    guide: GuideContent
    project_state: ProjectState
    role_context: RoleContext
    context_bundle: Any | None = None
    issues: list[dict] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
