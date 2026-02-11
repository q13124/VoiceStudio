"""
Issue-to-Task Generator.

Automatically creates task briefs from qualifying issues.
Used by the aggregator when issues meet auto-task criteria.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from tools.overseer.issues.models import Issue
    from tools.overseer.issues.store import IssueStore


# Role mapping based on instance type and category
INSTANCE_TYPE_TO_ROLE = {
    "agent": "Overseer (Role 0)",
    "engine": "Engine Engineer (Role 5)",
    "build": "Build & Tooling (Role 2)",
    "frontend": "UI Engineer (Role 3)",
    "backend": "Core Platform (Role 4)",
}

# Category-based role overrides
# Extended with comprehensive keyword mappings for issue classification
CATEGORY_TO_ROLE = {
    # UI Engineer (Role 3) - frontend, XAML, MVVM, visual elements
    "UI": "UI Engineer (Role 3)",
    "XAML": "UI Engineer (Role 3)",
    "MVVM": "UI Engineer (Role 3)",
    "VIEW": "UI Engineer (Role 3)",
    "VIEWMODEL": "UI Engineer (Role 3)",
    "PANEL": "UI Engineer (Role 3)",
    "BINDING": "UI Engineer (Role 3)",
    "LAYOUT": "UI Engineer (Role 3)",
    "THEME": "UI Engineer (Role 3)",
    "FLUENT": "UI Engineer (Role 3)",
    "WINUI": "UI Engineer (Role 3)",
    "CONTROL": "UI Engineer (Role 3)",
    "ANIMATION": "UI Engineer (Role 3)",

    # Build & Tooling (Role 2) - CI/CD, compilation, dependencies
    "BUILD": "Build & Tooling (Role 2)",
    "CI": "Build & Tooling (Role 2)",
    "CD": "Build & Tooling (Role 2)",
    "PIPELINE": "Build & Tooling (Role 2)",
    "COMPILE": "Build & Tooling (Role 2)",
    "MSBUILD": "Build & Tooling (Role 2)",
    "DOTNET": "Build & Tooling (Role 2)",
    "NUGET": "Build & Tooling (Role 2)",
    "PIP": "Build & Tooling (Role 2)",
    "DEPENDENCY": "Build & Tooling (Role 2)",
    "TOOLCHAIN": "Build & Tooling (Role 2)",
    "LINT": "Build & Tooling (Role 2)",
    "TEST": "Build & Tooling (Role 2)",
    "PYTEST": "Build & Tooling (Role 2)",
    "MSTEST": "Build & Tooling (Role 2)",

    # Engine Engineer (Role 5) - ML inference, audio processing, TTS/STT
    "ENGINE": "Engine Engineer (Role 5)",
    "SYNTHESIS": "Engine Engineer (Role 5)",
    "TRANSCRIPTION": "Engine Engineer (Role 5)",
    "TTS": "Engine Engineer (Role 5)",
    "STT": "Engine Engineer (Role 5)",
    "RVC": "Engine Engineer (Role 5)",
    "XTTS": "Engine Engineer (Role 5)",
    "WHISPER": "Engine Engineer (Role 5)",
    "MODEL": "Engine Engineer (Role 5)",
    "INFERENCE": "Engine Engineer (Role 5)",
    "AUDIO": "Engine Engineer (Role 5)",
    "VOICE": "Engine Engineer (Role 5)",
    "QUALITY": "Engine Engineer (Role 5)",
    "GPU": "Engine Engineer (Role 5)",
    "CUDA": "Engine Engineer (Role 5)",
    "TENSOR": "Engine Engineer (Role 5)",
    "TORCH": "Engine Engineer (Role 5)",

    # Core Platform (Role 4) - runtime, storage, services, backend
    "RUNTIME": "Core Platform (Role 4)",
    "STORAGE": "Core Platform (Role 4)",
    "BOOT": "Core Platform (Role 4)",
    "SERVICE": "Core Platform (Role 4)",
    "API": "Core Platform (Role 4)",
    "BACKEND": "Core Platform (Role 4)",
    "DATABASE": "Core Platform (Role 4)",
    "IPC": "Core Platform (Role 4)",
    "JOB": "Core Platform (Role 4)",
    "QUEUE": "Core Platform (Role 4)",
    "PREFLIGHT": "Core Platform (Role 4)",
    "CONFIG": "Core Platform (Role 4)",
    "SETTINGS": "Core Platform (Role 4)",

    # Release Engineer (Role 6) - packaging, installer, deployment
    "PACKAGING": "Release Engineer (Role 6)",
    "INSTALLER": "Release Engineer (Role 6)",
    "MSIX": "Release Engineer (Role 6)",
    "RELEASE": "Release Engineer (Role 6)",
    "DEPLOY": "Release Engineer (Role 6)",
    "VERSION": "Release Engineer (Role 6)",
    "UPDATE": "Release Engineer (Role 6)",
    "DISTRIBUTION": "Release Engineer (Role 6)",

    # System Architect (Role 1) - architecture, contracts, ADRs
    "ARCHITECTURE": "System Architect (Role 1)",
    "ADR": "System Architect (Role 1)",
    "CONTRACT": "System Architect (Role 1)",
    "BOUNDARY": "System Architect (Role 1)",
    "INTERFACE": "System Architect (Role 1)",
    "PROTOCOL": "System Architect (Role 1)",
    "SCHEMA": "System Architect (Role 1)",

    # Debug Agent (Role 7) - errors, exceptions, debugging
    "DEBUG": "Debug Agent (Role 7)",
    "ERROR": "Debug Agent (Role 7)",
    "EXCEPTION": "Debug Agent (Role 7)",
    "CRASH": "Debug Agent (Role 7)",
    "DIAGNOSTIC": "Debug Agent (Role 7)",
    "TRACEBACK": "Debug Agent (Role 7)",
    "STACKTRACE": "Debug Agent (Role 7)",
    "MEMORY": "Debug Agent (Role 7)",
    "LEAK": "Debug Agent (Role 7)",
    "HANG": "Debug Agent (Role 7)",
    "DEADLOCK": "Debug Agent (Role 7)",
    "TIMEOUT": "Debug Agent (Role 7)",
    "REGRESSION": "Debug Agent (Role 7)",

    # Overseer (Role 0) - governance, coordination, oversight
    "GOVERNANCE": "Overseer (Role 0)",
    "COORDINATION": "Overseer (Role 0)",
    "PRIORITY": "Overseer (Role 0)",
    "ESCALATION": "Overseer (Role 0)",
    "TASK": "Overseer (Role 0)",
    "WORKFLOW": "Overseer (Role 0)",
}

# Multi-role patterns: issues that span multiple domains
# Each pattern maps to a list of roles that should collaborate
MULTI_ROLE_PATTERNS = {
    # UI + Backend integration issues
    "API_BINDING": ["UI Engineer (Role 3)", "Core Platform (Role 4)"],
    "IPC_ERROR": ["UI Engineer (Role 3)", "Core Platform (Role 4)", "Debug Agent (Role 7)"],
    "WEBSOCKET": ["UI Engineer (Role 3)", "Core Platform (Role 4)"],

    # Engine + UI integration
    "ENGINE_UI": ["Engine Engineer (Role 5)", "UI Engineer (Role 3)"],
    "REALTIME_VOICE": ["Engine Engineer (Role 5)", "UI Engineer (Role 3)"],
    "QUALITY_DISPLAY": ["Engine Engineer (Role 5)", "UI Engineer (Role 3)"],

    # Build + Engine issues (dependency conflicts)
    "MODEL_DEPENDENCY": ["Engine Engineer (Role 5)", "Build & Tooling (Role 2)"],
    "CUDA_SETUP": ["Engine Engineer (Role 5)", "Build & Tooling (Role 2)"],
    "TORCH_VERSION": ["Engine Engineer (Role 5)", "Build & Tooling (Role 2)"],

    # Release + Build
    "INSTALLER_BUILD": ["Release Engineer (Role 6)", "Build & Tooling (Role 2)"],
    "PACKAGING_ERROR": ["Release Engineer (Role 6)", "Build & Tooling (Role 2)"],

    # Architecture reviews (cross-cutting)
    "BOUNDARY_VIOLATION": ["System Architect (Role 1)", "Overseer (Role 0)"],
    "CONTRACT_CHANGE": ["System Architect (Role 1)", "Core Platform (Role 4)"],

    # Debug escalation
    "CRITICAL_ERROR": ["Debug Agent (Role 7)", "Overseer (Role 0)"],
    "REGRESSION_TEST": ["Debug Agent (Role 7)", "Build & Tooling (Role 2)"],
}


class IssueRouter:
    """
    Multi-role issue router.
    
    Analyzes issue context and determines all relevant roles that should
    be involved, not just the primary owner.
    """

    @staticmethod
    def get_all_relevant_roles(issue: "Issue") -> list[str]:
        """
        Determine all roles that should be involved with an issue.
        
        Args:
            issue: The issue to analyze
            
        Returns:
            List of role names, with primary role first
        """
        roles = []
        seen_roles = set()

        # Check multi-role patterns first (combined keywords in message/context)
        message_upper = issue.message.upper() if issue.message else ""
        context_str = str(issue.context).upper() if issue.context else ""
        combined = f"{message_upper} {context_str}"

        for pattern, pattern_roles in MULTI_ROLE_PATTERNS.items():
            pattern_parts = pattern.split("_")
            if all(part in combined for part in pattern_parts):
                for role in pattern_roles:
                    if role not in seen_roles:
                        roles.append(role)
                        seen_roles.add(role)

        # Get primary role from category
        category = issue.category.upper() if issue.category else ""
        if category in CATEGORY_TO_ROLE:
            primary_role = CATEGORY_TO_ROLE[category]
            if primary_role not in seen_roles:
                roles.insert(0, primary_role)  # Primary goes first
                seen_roles.add(primary_role)

        # Get role from instance type as fallback
        instance_type = issue.instance_type.value if issue.instance_type else "agent"
        type_role = INSTANCE_TYPE_TO_ROLE.get(instance_type, "Overseer (Role 0)")
        if type_role not in seen_roles:
            roles.append(type_role)
            seen_roles.add(type_role)

        # Check for additional keywords in message that indicate other roles
        keyword_roles = IssueRouter._extract_keyword_roles(message_upper)
        for role in keyword_roles:
            if role not in seen_roles:
                roles.append(role)
                seen_roles.add(role)

        return roles if roles else ["Overseer (Role 0)"]

    @staticmethod
    def _extract_keyword_roles(message: str) -> list[str]:
        """Extract additional roles based on keywords in the message."""
        roles = []
        
        # Map of keywords to roles for secondary involvement
        keyword_map = {
            "BUILD FAIL": "Build & Tooling (Role 2)",
            "TEST FAIL": "Build & Tooling (Role 2)",
            "UI FREEZE": "UI Engineer (Role 3)",
            "PANEL CRASH": "UI Engineer (Role 3)",
            "ENGINE ERROR": "Engine Engineer (Role 5)",
            "SYNTHESIS FAIL": "Engine Engineer (Role 5)",
            "API TIMEOUT": "Core Platform (Role 4)",
            "SERVICE UNAVAILABLE": "Core Platform (Role 4)",
            "INSTALLER FAIL": "Release Engineer (Role 6)",
            "PACKAGE ERROR": "Release Engineer (Role 6)",
        }

        for keyword, role in keyword_map.items():
            if keyword in message:
                if role not in roles:
                    roles.append(role)

        return roles

    @staticmethod
    def get_primary_role(issue: "Issue") -> str:
        """Get the primary owner role for an issue."""
        roles = IssueRouter.get_all_relevant_roles(issue)
        return roles[0] if roles else "Overseer (Role 0)"

    @staticmethod
    def get_collaborators(issue: "Issue") -> list[str]:
        """Get collaborator roles (excluding primary)."""
        roles = IssueRouter.get_all_relevant_roles(issue)
        return roles[1:] if len(roles) > 1 else []

    @staticmethod
    def requires_escalation(issue: "Issue") -> bool:
        """Check if issue requires Overseer escalation."""
        roles = IssueRouter.get_all_relevant_roles(issue)
        # Escalate if multiple roles needed or high severity
        if len(roles) > 2:
            return True
        if issue.severity and issue.severity.value in ("critical", "high"):
            return True
        return False


class IssueToTaskGenerator:
    """
    Generates task brief files from Issue objects.
    
    Task IDs are auto-incremented based on existing files in docs/tasks/.
    Uses TASK_TEMPLATE.md structure for consistency.
    """

    def __init__(
        self,
        issue_store: Optional[IssueStore] = None,
        tasks_dir: Optional[Path] = None,
    ):
        """
        Initialize the generator.
        
        Args:
            issue_store: Optional IssueStore for querying related issues.
            tasks_dir: Directory for task files (default: docs/tasks).
        """
        self.store = issue_store
        self.tasks_dir = tasks_dir or Path("docs/tasks")
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

    def _next_task_id(self) -> str:
        """
        Determine the next available TASK-NNNN ID.
        
        Scans existing task files and returns the next sequential ID.
        """
        existing_ids: list[int] = []
        pattern = re.compile(r"^TASK-(\d{4})\.md$", re.IGNORECASE)
        
        for path in self.tasks_dir.iterdir():
            match = pattern.match(path.name)
            if match:
                existing_ids.append(int(match.group(1)))
        
        next_num = max(existing_ids, default=0) + 1
        return f"TASK-{next_num:04d}"

    def _determine_owner_role(self, issue: Issue) -> str:
        """Determine the owner role based on issue properties."""
        return IssueRouter.get_primary_role(issue)

    def _determine_collaborators(self, issue: Issue) -> list[str]:
        """Determine collaborator roles that should be involved."""
        return IssueRouter.get_collaborators(issue)

    def _requires_escalation(self, issue: Issue) -> bool:
        """Check if issue requires Overseer escalation."""
        return IssueRouter.requires_escalation(issue)

    def _render_template(self, issue: Issue, task_id: str) -> str:
        """
        Render the task brief markdown from an issue.
        
        Uses a format compatible with TASK_TEMPLATE.md.
        """
        owner_role = self._determine_owner_role(issue)
        collaborators = self._determine_collaborators(issue)
        requires_escalation = self._requires_escalation(issue)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Build affected modules from context
        affected_modules = []
        if issue.context.get("_error_codes"):
            for code in issue.context["_error_codes"][:3]:
                affected_modules.append(f"- [ ] Error code: {code}")
        if issue.context.get("traceback"):
            affected_modules.append("- [ ] Stack trace analysis required")
        if not affected_modules:
            affected_modules.append("- [ ] TBD based on investigation")
        
        # Build constraints
        constraints = [
            "- No breaking changes to existing API",
            "- Must pass verification suite after fix",
            "- Follow closure protocol for completion",
        ]
        
        # Build proofs
        proofs = [
            "- [ ] Build succeeds (`dotnet build` / `python -m pytest`)",
            "- [ ] `python scripts/run_verification.py` all PASS",
            "- [ ] Issue marked resolved in issue store",
        ]
        
        # Build acceptance criteria
        acceptance = [
            f"- [ ] Root cause identified for: {issue.error_type}",
            "- [ ] Fix implemented and tested",
            "- [ ] No regression in affected area",
            "- [ ] STATE.md updated with completion",
        ]
        
        content = f"""# {task_id}: Fix {issue.error_type} - {issue.message[:60]}

## Objective

Resolve {issue.severity.value.upper()} severity issue automatically detected by the Overseer issue system.

**Issue ID**: `{issue.id}`  
**Pattern Hash**: `{issue.pattern_hash}`  
**Detected**: {issue.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Instance**: {issue.instance_type.value} / {issue.instance_id}

### Error Details

```
{issue.message[:500]}
```

## Affected Modules

{chr(10).join(affected_modules)}

## Constraints

{chr(10).join(constraints)}

## Required Proofs

{chr(10).join(proofs)}

## Acceptance Criteria

{chr(10).join(acceptance)}

## Tech Debt

- Auto-generated from issue `{issue.id}` — review for tech debt patterns

## Owner

- **{owner_role}** — Primary owner, investigate and resolve
{self._format_collaborators(collaborators)}
{self._format_escalation(requires_escalation)}

## Status

- [x] Not Started
- [ ] In Progress
- [ ] Blocked
- [ ] Complete

**Execution Summary**: Auto-created on {timestamp} from issue system. Awaiting assignment.

## Context

<details>
<summary>Issue Context (click to expand)</summary>

```json
{self._safe_json_context(issue.context)}
```

</details>
"""
        return content

    def _format_collaborators(self, collaborators: list[str]) -> str:
        """Format collaborator roles for the template."""
        if not collaborators:
            return ""
        lines = ["### Collaborators"]
        for role in collaborators:
            lines.append(f"- **{role}** — Review and assist")
        return "\n" + "\n".join(lines)

    def _format_escalation(self, requires_escalation: bool) -> str:
        """Format escalation note if needed."""
        if not requires_escalation:
            return ""
        return "\n> **Note**: This issue requires Overseer coordination due to cross-domain complexity."

    def _safe_json_context(self, context: dict) -> str:
        """Safely serialize context to JSON, handling special types."""
        import json
        
        # Filter sensitive keys and limit size
        filtered = {}
        for key, value in context.items():
            if key.startswith("_"):
                continue  # Skip internal keys
            if isinstance(value, str) and len(value) > 1000:
                value = value[:1000] + "... [truncated]"
            filtered[key] = value
        
        try:
            return json.dumps(filtered, indent=2, default=str)
        except Exception:
            return "{}"

    def create_task_file(self, issue: Issue) -> Path:
        """
        Create a task brief file from an issue.
        
        Args:
            issue: The Issue to create a task from.
            
        Returns:
            Path to the created task file.
        """
        task_id = self._next_task_id()
        content = self._render_template(issue, task_id)
        
        path = self.tasks_dir / f"{task_id}.md"
        path.write_text(content, encoding="utf-8")
        
        return path

    def link_issue_to_task(self, issue_id: str, task_id: str) -> bool:
        """
        Update an issue to link it to a task.
        
        Note: This requires the issue store to be provided during init.
        
        Args:
            issue_id: The issue ID to update.
            task_id: The task ID to link.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.store:
            return False
        
        # Get the issue by ID using the correct API
        issue = self.store.get_by_id(issue_id)
        if not issue:
            return False
        
        issue.context["linked_task"] = task_id
        issue.context["task_linked_at"] = datetime.now(timezone.utc).isoformat()
        
        # Re-append with updated context (store handles dedup by ID)
        self.store.append(issue)
        return True
