from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional

from tools.onboarding.core.models import OnboardingPacket, RoleConfig
from tools.onboarding.core.role_registry import RoleRegistry
from tools.onboarding.sources.context_source import RoleContextSource
from tools.onboarding.sources.guide_source import GuideSource
from tools.onboarding.sources.prompt_source import PromptSource
from tools.onboarding.sources.state_source import StateSource

if TYPE_CHECKING:
    from tools.context.core.manager import ContextManager
    from tools.overseer.agent.registry import AgentRegistry


DEFAULT_ONBOARDING_CONFIG = Path("tools/onboarding/config/onboarding.json")
DEFAULT_TEMPLATE_PATH = Path("tools/onboarding/templates/onboarding_packet.md.j2")
DEFAULT_CONTEXT_CONFIG = Path("tools/context/config/context-sources.json")


def _default_agent_registry() -> Optional["AgentRegistry"]:
    """Return AgentRegistry if VOICESTUDIO_REGISTER_AGENT_ON_ONBOARD=1, else None."""
    if os.environ.get("VOICESTUDIO_REGISTER_AGENT_ON_ONBOARD", "").strip() == "1":
        try:
            from tools.overseer.agent.registry import AgentRegistry
            return AgentRegistry()
        except Exception:
            return None
    return None


def _default_context_manager() -> Optional["ContextManager"]:
    """Build ContextManager from default config when integration is enabled."""
    try:
        from tools.context.core.manager import ContextManager
        root = Path(__file__).resolve().parents[3]
        cfg = root / DEFAULT_CONTEXT_CONFIG
        if cfg.exists():
            return ContextManager.from_config(cfg)
    # ALLOWED: bare except - Best effort context manager init
    except Exception:
        pass
    return None


class OnboardingAssembler:
    """Facade for assembling role onboarding packets."""

    def __init__(
        self,
        config_path: Path = DEFAULT_ONBOARDING_CONFIG,
        agent_registry: Optional["AgentRegistry"] = None,
        context_manager: Optional["ContextManager"] = None,
    ):
        self._config_path = config_path
        self._config = self._load_config(config_path)
        self._agent_registry = agent_registry if agent_registry is not None else _default_agent_registry()
        self._context_manager = (
            context_manager
            if context_manager is not None
            else _default_context_manager()
        )
        self.registry = RoleRegistry.from_config()
        self.prompt_source = PromptSource(
            self.registry,
            max_identity_chars=self._config.get("prompt_identity_max_chars", 1800),
            max_summary_chars=self._config.get("prompt_summary_max_chars", 1200),
        )
        self.guide_source = GuideSource(
            self.registry,
            max_chars=self._config.get("guide_summary_max_chars", 3200),
        )
        self.state_source = StateSource()
        self.context_source = RoleContextSource(
            blockers_limit=self._config.get("blockers_limit", 8),
        )
        self.template_path = DEFAULT_TEMPLATE_PATH

    def _load_config(self, config_path: Path) -> dict:
        path = config_path if config_path.is_absolute() else Path(__file__).resolve().parents[3] / config_path
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _fetch_role_issues(self, role_id: str) -> List[Any]:
        """
        Fetch issues assigned to or relevant for this role.

        Returns list of Issue objects from handoff queue.
        """
        try:
            from tools.overseer.issues.handoff import HandoffQueue

            queue = HandoffQueue()
            entries = queue.get_role_queue(role_id, unacknowledged_only=True)

            # Convert entries to simplified issue dicts
            issues = []
            for entry in entries[:10]:  # Limit to 10 most recent
                issues.append({
                    "id": entry["issue_id"],
                    "severity": entry["severity"],
                    "status": entry["status"],
                    "message": entry["message"],
                    "instance_type": entry["instance_type"],
                    "correlation_id": entry["correlation_id"],
                    "handed_off_at": entry["handed_off_at"],
                })

            return issues

        except Exception as e:
            # Graceful degradation
            return []

    def assemble(self, role_id: str, include_full_guide: Optional[bool] = None) -> OnboardingPacket:
        """
        Assemble onboarding packet for role.
        
        Integrates with:
        - RoleRegistry: Role config and metadata
        - StateSource: Project state and active task
        - ContextManager: Context bundle allocation (ADR-015)
        - AgentRegistry: Agent registration when enabled
        - PolicyEngine: Role permission validation (via AgentRegistry)
        
        Args:
            role_id: Role ID or alias (0-7, or short-name)
            include_full_guide: Include full role guide in packet
        
        Returns:
            OnboardingPacket with all components
            
        Raises:
            ValueError: If role_id unknown or policy validation fails
        """
        role = self.registry.get_role(role_id)
        include_full = (
            include_full_guide
            if include_full_guide is not None
            else bool(self._config.get("include_full_guide_default", False))
        )

        # Load role-specific content
        prompt = self.prompt_source.load(role)
        guide = self.guide_source.summarize(role, include_full=include_full)
        project_state, active_task = self.state_source.load()
        role_context = self.context_source.load(role, active_task=active_task)

        # Allocate context bundle (ADR-015: Integration Contract)
        context_bundle = None
        if self._context_manager is not None:
            try:
                from tools.context.core.models import AllocationContext, ContextLevel
                ctx = AllocationContext(
                    task_id=active_task.id if active_task else None,
                    phase=project_state.phase,
                    role=role.short_name,
                    include_git=False,
                    max_level=ContextLevel.MID,  # Brief + Ledger, skip low-priority sources
                )
                context_bundle = self._context_manager.allocate(ctx)
            except Exception as e:
                # Graceful degradation (ADR-015: failure mode)
                import logging
                logging.getLogger(__name__).debug(
                    "Context Manager unavailable during onboarding: %s", e
                )

        # Fetch role-specific issues from handoff queue
        role_issues = self._fetch_role_issues(role_id)

        # Validate packet before creating
        validation_errors = self._validate_packet_components(
            role, prompt, guide, project_state
        )
        if validation_errors:
            import logging
            for error in validation_errors:
                logging.getLogger(__name__).warning("Packet validation: %s", error)

        packet = OnboardingPacket(
            role=role,
            prompt=prompt,
            guide=guide,
            project_state=project_state,
            role_context=role_context,
            context_bundle=context_bundle,
            issues=role_issues,
        )

        # Register agent with policy validation (ADR-003: Agent Governance)
        if self._agent_registry is not None:
            try:
                from tools.overseer.agent.identity import AgentIdentity
                from tools.overseer.agent.role_mapping import role_to_agent_role
                import logging
                
                ar = role_to_agent_role(role_id)
                identity = AgentIdentity.create(role=ar, user_id="voicestudio")
                
                # Policy validation would happen here via PolicyEngine if integrated
                # For now, registry.register performs basic validation
                self._agent_registry.register(identity)
                logging.getLogger(__name__).info(
                    "Agent registered: %s (role=%s)", identity.agent_id, ar.value
                )
            except ValueError as ve:
                # Agent already registered or validation failed
                import logging
                logging.getLogger(__name__).warning("Agent registration: %s", ve)
            except Exception as e:
                # Graceful degradation (ADR-015: failure mode)
                import logging
                logging.getLogger(__name__).debug(
                    "Agent registry unavailable during onboarding: %s", e
                )

        return packet
    
    def _validate_packet_components(
        self, role, prompt, guide, project_state
    ) -> List[str]:
        """
        Validate packet completeness.
        
        Returns list of validation errors (empty if valid).
        """
        errors = []
        
        if not role or not role.id:
            errors.append("Role missing or invalid")
        if not prompt or not prompt.full_text:
            errors.append(f"Prompt missing for role {role.id if role else 'unknown'}")
        if not guide:
            errors.append(f"Guide missing for role {role.id if role else 'unknown'}")
        if not project_state:
            errors.append("Project state unavailable")
        
        return errors

    def render(self, packet: OnboardingPacket) -> str:
        template_text = self._read_template()
        if template_text:
            rendered = self._render_with_jinja(template_text, packet)
            if rendered:
                return rendered
        return self._render_fallback(packet)

    def _read_template(self) -> str:
        root = Path(__file__).resolve().parents[3]
        path = root / self.template_path
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def _render_with_jinja(self, template_text: str, packet: OnboardingPacket) -> str:
        try:
            from jinja2 import Environment
        except Exception:
            return ""
        env = Environment(autoescape=False)
        template = env.from_string(template_text)
        context_bundle_preamble = ""
        if packet.context_bundle is not None and hasattr(packet.context_bundle, "to_preamble_markdown"):
            context_bundle_preamble = packet.context_bundle.to_preamble_markdown()
        return template.render(
            role=packet.role,
            prompt=packet.prompt,
            guide=packet.guide,
            state=packet.project_state,
            context=packet.role_context,
            timestamp=packet.generated_at,
            context_bundle=packet.context_bundle,
            context_bundle_preamble=context_bundle_preamble,
        )

    def _render_fallback(self, packet: OnboardingPacket) -> str:
        role = packet.role
        state = packet.project_state
        context = packet.role_context
        guide = packet.guide
        prompt = packet.prompt

        lines = [
            f"# {role.name} Onboarding Packet",
            "",
            f"> Generated: {packet.generated_at}",
            "",
            "## Role Identity",
            "",
            prompt.identity_section.strip() or "(No role identity section found.)",
            "",
            "## Current Project State",
            "",
            f"- **Phase**: {state.phase or 'Unknown'}",
            f"- **Active Gate**: {state.active_gate or 'Unknown'}",
            f"- **Active Task**: {state.active_task_id or 'None'} {('— ' + state.active_task_title) if state.active_task_title else ''}",
            "",
            "## Your Responsibilities",
            "",
            f"### Primary Gates: {', '.join(role.primary_gates) if role.primary_gates else 'None'}",
            "",
            guide.summary.strip() or "(No guide summary available.)",
        ]

        if guide.full_text:
            lines += [
                "",
                "## Full Role Guide",
                "",
                guide.full_text.strip(),
            ]

        lines += [
            "",
            "## Current Blockers for Your Gates",
            "",
        ]

        if context.blockers:
            for blocker in context.blockers:
                lines.append(
                    f"- **{blocker.id}** ({blocker.severity}) Gate {blocker.gate} — {blocker.title} (Owner: {blocker.owner_role})"
                )
        else:
            lines.append("- None")

        # Add issues section
        if packet.issues:
            lines += [
                "",
                f"## Active Issues Assigned to You ({len(packet.issues)})",
                "",
            ]
            for issue in packet.issues:
                msg = issue.get("message", "")
                msg_short = msg[:80] + ("..." if len(msg) > 80 else "")
                lines.append(
                    f"- **{issue.get('id')}** [{issue.get('severity', '').upper()}]: {msg_short}"
                )
                lines.append(
                    f"  - Status: {issue.get('status')} | Type: {issue.get('instance_type')}"
                )
                lines.append(
                    f"  - Correlation: {issue.get('correlation_id')}"
                )
            lines.append("")
            lines.append("Use `python -m tools.overseer.cli.main issues get <issue-id>` for details.")

        lines += [
            "",
            "## Next Actions",
            "",
            prompt.next_actions.strip() or "See role prompt for next actions.",
            "",
            "## Full Role Prompt",
            "",
            prompt.full_text.strip(),
            "",
        ]

        if packet.context_bundle is not None and hasattr(packet.context_bundle, "to_preamble_markdown"):
            lines += ["", packet.context_bundle.to_preamble_markdown(), ""]

        return "\n".join(lines)
