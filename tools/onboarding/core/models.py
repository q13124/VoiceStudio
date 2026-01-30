from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional


@dataclass
class RoleConfig:
    id: str
    short_name: str
    name: str
    prompt_path: str
    guide_path: Optional[str] = None
    primary_gates: List[str] = field(default_factory=list)


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
    phase: Optional[str] = None
    active_gate: Optional[str] = None
    active_task_id: Optional[str] = None
    active_task_title: Optional[str] = None


@dataclass
class ActiveTask:
    id: Optional[str] = None
    title: Optional[str] = None
    priority: Optional[str] = None
    blockers: Optional[str] = None


@dataclass
class Blocker:
    id: str
    severity: str
    gate: str
    title: str
    owner_role: str


@dataclass
class RoleContext:
    blockers: List[Blocker] = field(default_factory=list)


@dataclass
class OnboardingPacket:
    role: RoleConfig
    prompt: PromptContent
    guide: GuideContent
    project_state: ProjectState
    role_context: RoleContext
    context_bundle: Optional[Any] = None
    issues: List[dict] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
