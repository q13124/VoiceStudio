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
CATEGORY_TO_ROLE = {
    "UI": "UI Engineer (Role 3)",
    "BUILD": "Build & Tooling (Role 2)",
    "ENGINE": "Engine Engineer (Role 5)",
    "RUNTIME": "Core Platform (Role 4)",
    "STORAGE": "Core Platform (Role 4)",
    "PACKAGING": "Release Engineer (Role 6)",
    "BOOT": "Core Platform (Role 4)",
    # Debug Role (Role 7) - handles errors, exceptions, and debugging tasks
    "DEBUG": "Debug Agent (Role 7)",
    "ERROR": "Debug Agent (Role 7)",
    "EXCEPTION": "Debug Agent (Role 7)",
    "CRASH": "Debug Agent (Role 7)",
    "DIAGNOSTIC": "Debug Agent (Role 7)",
}


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
        # Check category first (more specific)
        category = issue.category.upper() if issue.category else ""
        if category in CATEGORY_TO_ROLE:
            return CATEGORY_TO_ROLE[category]
        
        # Fall back to instance type
        instance_type = issue.instance_type.value if issue.instance_type else "agent"
        return INSTANCE_TYPE_TO_ROLE.get(instance_type, "Overseer (Role 0)")

    def _render_template(self, issue: Issue, task_id: str) -> str:
        """
        Render the task brief markdown from an issue.
        
        Uses a format compatible with TASK_TEMPLATE.md.
        """
        owner_role = self._determine_owner_role(issue)
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

- **{owner_role}** — Investigate and resolve

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
        
        # Query the issue
        issues = list(self.store.query(filters={"id": issue_id}))
        if not issues:
            return False
        
        issue = issues[0]
        issue.context["linked_task"] = task_id
        issue.context["task_linked_at"] = datetime.now(timezone.utc).isoformat()
        
        # Re-append with updated context (store handles dedup by ID)
        self.store.append(issue)
        return True
