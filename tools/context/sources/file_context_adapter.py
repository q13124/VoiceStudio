"""
File Context Adapter for VoiceStudio.

Detects which language/stack is active based on:
- Git status (modified/staged files)
- Active directory context
- Task brief scope

Injects language-specific reminders to prevent cross-stack confusion.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.sources.base import BaseSourceAdapter


@dataclass
class LanguageContext:
    """Language context for injection."""

    primary_language: str  # "csharp", "python", "mixed"
    stack: str  # "frontend", "backend", "engine", "mixed"
    files_detected: list[str] = field(default_factory=list)
    reminder: str = ""
    conventions_file: str | None = None


# File pattern to language/stack mapping
FILE_PATTERNS: dict[str, dict[str, str]] = {
    # C# / WinUI Frontend
    ".cs": {"language": "csharp", "stack": "frontend"},
    ".xaml": {"language": "csharp", "stack": "frontend"},
    ".csproj": {"language": "csharp", "stack": "frontend"},

    # Python Backend
    ".py": {"language": "python", "stack": "backend"},

    # Engine layer (Python but distinct)
    "_engine.py": {"language": "python", "stack": "engine"},
}

# Directory to stack mapping (more specific)
DIRECTORY_PATTERNS: dict[str, dict[str, str]] = {
    "src/VoiceStudio.App": {"language": "csharp", "stack": "frontend"},
    "src/VoiceStudio.Core": {"language": "csharp", "stack": "frontend"},
    "backend/": {"language": "python", "stack": "backend"},
    "app/core/engines": {"language": "python", "stack": "engine"},
    "engines/": {"language": "python", "stack": "engine"},
    "tests/": {"language": "python", "stack": "backend"},
}

# Language-specific reminders
LANGUAGE_REMINDERS: dict[str, str] = {
    "csharp": """
**ACTIVE STACK: C# / WinUI 3 Frontend**
- Use PascalCase for methods, _camelCase for private fields
- Use `null` not `None`, `{ }` not `pass`
- Use `{x:Bind}` for XAML bindings
- Async methods end in `Async`, return `Task<T>`
- See `.cursor/rules/languages/csharp-winui.mdc` for full conventions
""".strip(),

    "python": """
**ACTIVE STACK: Python 3.9+ Backend**
- Use snake_case for functions/variables, PascalCase for classes
- Use `None` not `null`, `pass` for empty blocks
- Add type hints to all functions
- Use `async def` with `await` for async operations
- See `.cursor/rules/languages/python-backend.mdc` for full conventions
""".strip(),

    "mixed": """
**ACTIVE STACK: Mixed (C# + Python)**
- C# files: PascalCase methods, `null`, `{x:Bind}`, `async Task`
- Python files: snake_case functions, `None`, type hints, `async def`
- Do NOT mix conventions between stacks!
- See `.cursor/rules/languages/` for stack-specific conventions
""".strip(),
}


class FileContextAdapter(BaseSourceAdapter):
    """
    Detects active language/stack and injects reminders.

    Uses git status to determine which files are being worked on,
    then classifies by language and provides appropriate reminders.
    """

    def __init__(self, offline: bool = True):
        super().__init__(
            source_name="file_context",
            priority=100,  # High priority - language context is critical
            offline=offline,
        )

    def fetch(self, context: AllocationContext) -> SourceResult:
        def _load() -> dict[str, Any]:
            # Get modified files from git status
            modified_files = self._get_modified_files()

            # Classify files by language/stack
            language_context = self._classify_files(modified_files)

            return {
                "file_context": language_context,
                "language_reminder": language_context.reminder,
            }

        return self._measure(_load, context)

    def _get_modified_files(self) -> list[str]:
        """Get list of modified/staged files from git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=Path(__file__).resolve().parents[3],  # Repo root (tools/context/sources -> VoiceStudio)
            )

            if result.returncode != 0:
                return []

            files = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                # Format: "XY filename" or "XY original -> renamed"
                parts = line[3:].strip().split(" -> ")
                filename = parts[-1].strip()
                if filename:
                    files.append(filename)

            return files

        except Exception:
            return []

    def _classify_files(self, files: list[str]) -> LanguageContext:
        """Classify files by language and stack."""
        if not files:
            return LanguageContext(
                primary_language="unknown",
                stack="unknown",
                reminder="",
            )

        languages: set[str] = set()
        stacks: set[str] = set()
        classified_files: list[str] = []

        for filepath in files:
            classification = self._classify_single_file(filepath)
            if classification:
                languages.add(classification["language"])
                stacks.add(classification["stack"])
                classified_files.append(filepath)

        # Determine primary language
        if len(languages) == 0:
            primary_language = "unknown"
        elif len(languages) == 1:
            primary_language = next(iter(languages))
        else:
            primary_language = "mixed"

        # Determine primary stack
        if len(stacks) == 0:
            stack = "unknown"
        elif len(stacks) == 1:
            stack = next(iter(stacks))
        else:
            stack = "mixed"

        # Get reminder
        reminder = LANGUAGE_REMINDERS.get(primary_language, "")

        # Get conventions file
        conventions_map = {
            "csharp": ".cursor/rules/languages/csharp-winui.mdc",
            "python": ".cursor/rules/languages/python-backend.mdc",
        }
        conventions_file = conventions_map.get(primary_language)

        return LanguageContext(
            primary_language=primary_language,
            stack=stack,
            files_detected=classified_files[:10],  # Limit for context size
            reminder=reminder,
            conventions_file=conventions_file,
        )

    def _classify_single_file(self, filepath: str) -> dict[str, str] | None:
        """Classify a single file by its path."""
        filepath_lower = filepath.lower().replace("\\", "/")

        # Check directory patterns first (more specific)
        for pattern, classification in DIRECTORY_PATTERNS.items():
            if pattern.lower() in filepath_lower:
                return classification

        # Check file extension patterns
        for pattern, classification in FILE_PATTERNS.items():
            if filepath_lower.endswith(pattern.lower()):
                return classification

        return None

    def estimate_size(self, context: AllocationContext) -> int:
        """Estimate size of language context."""
        return 500  # Reminders are compact


def get_language_reminder_for_file(filepath: str) -> str:
    """
    Convenience function to get language reminder for a specific file.

    Can be called directly without full context allocation.
    """
    adapter = FileContextAdapter()
    classification = adapter._classify_single_file(filepath)

    if not classification:
        return ""

    language = classification["language"]
    return LANGUAGE_REMINDERS.get(language, "")
