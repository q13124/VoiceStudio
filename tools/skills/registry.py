"""
Skill Registry for VoiceStudio.

Discovers, manages, and provides access to skills in .cursor/skills/.
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class SkillCategory(str, Enum):
    """Skill categories."""

    ROLES = "roles"
    TOOLS = "tools"


@dataclass
class Skill:
    """Represents a registered skill."""

    name: str
    category: SkillCategory
    path: Path
    description: str = ""
    display_name: str = ""
    has_script: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def skill_md_path(self) -> Path:
        """Path to SKILL.md file."""
        return self.path / "SKILL.md"

    @property
    def invoke_script_path(self) -> Path | None:
        """Path to invoke.py script, if exists."""
        script_path = self.path / "scripts" / "invoke.py"
        return script_path if script_path.exists() else None

    @property
    def full_id(self) -> str:
        """Full skill identifier (e.g., roles/build-tooling)."""
        return f"{self.category.value}/{self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "category": self.category.value,
            "path": str(self.path),
            "description": self.description,
            "display_name": self.display_name,
            "has_script": self.has_script,
            "metadata": self.metadata,
        }


class SkillRegistry:
    """
    Registry for discovering and managing skills.

    Skills are stored in .cursor/skills/ with the following structure:

    .cursor/skills/
        roles/
            build-tooling/
                SKILL.md
                scripts/
                    invoke.py
        tools/
            gate-status/
                SKILL.md
                scripts/
                    invoke.py
    """

    def __init__(self, skills_root: Path | None = None):
        """
        Initialize the registry.

        Args:
            skills_root: Root directory for skills (default: .cursor/skills/)
        """
        self._skills_root = skills_root or self._find_skills_root()
        self._skills: dict[str, Skill] = {}
        self._lock = threading.RLock()
        self._loaded = False

    @staticmethod
    def _find_skills_root() -> Path:
        """Find the skills root directory."""
        # Try relative to this file
        module_path = Path(__file__).resolve()
        for parent in module_path.parents:
            candidate = parent / ".cursor" / "skills"
            if candidate.exists():
                return candidate

        # Fallback to workspace root
        return Path(".cursor/skills")

    def _discover_skills(self) -> None:
        """Discover all skills in the skills root."""
        with self._lock:
            self._skills.clear()

            if not self._skills_root.exists():
                return

            for category in SkillCategory:
                category_dir = self._skills_root / category.value
                if not category_dir.exists():
                    continue

                for skill_dir in category_dir.iterdir():
                    if not skill_dir.is_dir():
                        continue

                    skill_md = skill_dir / "SKILL.md"
                    if not skill_md.exists():
                        continue

                    skill = self._parse_skill(skill_dir, category)
                    if skill:
                        self._skills[skill.full_id] = skill

            self._loaded = True

    def _parse_skill(self, skill_dir: Path, category: SkillCategory) -> Skill | None:
        """Parse a skill from its directory."""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None

        name = skill_dir.name
        description = ""
        display_name = name.replace("-", " ").title()

        # Parse SKILL.md for metadata
        try:
            content = skill_md.read_text(encoding="utf-8")

            # Extract title (first # heading)
            title_match = re.search(r"^#\s+(.+?)(?:\s+Skill)?$", content, re.MULTILINE)
            if title_match:
                display_name = title_match.group(1).strip()

            # Extract description (first paragraph after Description heading)
            desc_match = re.search(
                r"##\s+Description\s*\n+(.+?)(?:\n\n|\n##)",
                content,
                re.DOTALL | re.IGNORECASE,
            )
            if desc_match:
                description = desc_match.group(1).strip()
                # Take first sentence or first 200 chars
                if len(description) > 200:
                    description = description[:200].rsplit(" ", 1)[0] + "..."

        # ALLOWED: bare except - skill parsing failure should not prevent skill discovery
        except Exception as e:
            import logging
            logging.getLogger(__name__).debug(f"Failed to parse skill metadata for {name}: {e}")

        has_script = (skill_dir / "scripts" / "invoke.py").exists()

        return Skill(
            name=name,
            category=category,
            path=skill_dir,
            description=description,
            display_name=display_name,
            has_script=has_script,
        )

    def get_all(self) -> list[Skill]:
        """Get all registered skills."""
        if not self._loaded:
            self._discover_skills()

        with self._lock:
            return list(self._skills.values())

    def get(self, skill_id: str) -> Skill | None:
        """
        Get a skill by ID.

        Args:
            skill_id: Full skill ID (e.g., "roles/build-tooling") or name only

        Returns:
            Skill or None if not found
        """
        if not self._loaded:
            self._discover_skills()

        with self._lock:
            # Try exact match first
            if skill_id in self._skills:
                return self._skills[skill_id]

            # Try matching by name only
            for skill in self._skills.values():
                if skill.name == skill_id:
                    return skill

            return None

    def get_by_category(self, category: SkillCategory) -> list[Skill]:
        """Get all skills in a category."""
        if not self._loaded:
            self._discover_skills()

        with self._lock:
            return [s for s in self._skills.values() if s.category == category]

    def refresh(self) -> int:
        """
        Refresh the skill registry by re-discovering skills.

        Returns:
            Number of skills discovered
        """
        self._loaded = False
        self._discover_skills()
        return len(self._skills)

    def register(
        self,
        name: str,
        category: SkillCategory,
        description: str = "",
        display_name: str = "",
        with_script: bool = False,
    ) -> Skill:
        """
        Register a new skill.

        Creates the skill directory structure and SKILL.md file.

        Args:
            name: Skill name (kebab-case)
            category: Skill category
            description: Short description
            display_name: Human-readable name
            with_script: Whether to create invoke.py template

        Returns:
            The created Skill

        Raises:
            ValueError: If skill name is invalid or already exists
        """
        # Validate name
        if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$", name):
            raise ValueError(
                f"Invalid skill name '{name}'. Use kebab-case (e.g., my-skill)"
            )

        skill_dir = self._skills_root / category.value / name

        if skill_dir.exists():
            raise ValueError(f"Skill already exists: {name}")

        # Create directories
        skill_dir.mkdir(parents=True, exist_ok=True)

        if not display_name:
            display_name = name.replace("-", " ").title()

        # Create SKILL.md
        skill_md_content = f"""# {display_name} Skill

## Description

{description or "Add description here."}

## When to Use

Use this skill when:
- [Describe use cases]

## Usage

```
@skill-{category.value}-{name}
```

## Capabilities

- [List key capabilities]
"""
        (skill_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")

        # Create scripts if requested
        if with_script:
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            (scripts_dir / "__init__.py").write_text(
                f"# {display_name} skill scripts\n", encoding="utf-8"
            )

            invoke_content = f'''"""
{display_name} Skill Invoke Script
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = {{"skill": "{name}", "status": "ok"}}

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[{name}] Skill executed successfully")

    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
            (scripts_dir / "invoke.py").write_text(invoke_content, encoding="utf-8")

        # Create skill object
        skill = Skill(
            name=name,
            category=category,
            path=skill_dir,
            description=description,
            display_name=display_name,
            has_script=with_script,
        )

        # Add to cache
        with self._lock:
            self._skills[skill.full_id] = skill

        return skill


# Global registry instance
_registry_instance: SkillRegistry | None = None
_registry_lock = threading.Lock()


def get_registry() -> SkillRegistry:
    """Get or create the global skill registry."""
    global _registry_instance

    with _registry_lock:
        if _registry_instance is None:
            _registry_instance = SkillRegistry()
        return _registry_instance


def list_skills(category: str | None = None) -> list[Skill]:
    """
    List all skills, optionally filtered by category.

    Args:
        category: Optional category filter ("roles" or "tools")

    Returns:
        List of skills
    """
    registry = get_registry()

    if category:
        try:
            cat = SkillCategory(category)
            return registry.get_by_category(cat)
        except ValueError:
            return []

    return registry.get_all()


def get_skill(skill_id: str) -> Skill | None:
    """
    Get a skill by ID or name.

    Args:
        skill_id: Skill ID (e.g., "roles/build-tooling") or name ("build-tooling")

    Returns:
        Skill or None
    """
    return get_registry().get(skill_id)


def register_skill(
    name: str,
    category: str,
    description: str = "",
    display_name: str = "",
    with_script: bool = False,
) -> Skill:
    """
    Register a new skill.

    Args:
        name: Skill name (kebab-case)
        category: "roles" or "tools"
        description: Short description
        display_name: Human-readable name
        with_script: Create invoke.py template

    Returns:
        Created Skill
    """
    cat = SkillCategory(category)
    return get_registry().register(
        name=name,
        category=cat,
        description=description,
        display_name=display_name,
        with_script=with_script,
    )
