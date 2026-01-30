"""
Memory Tools

Governed memory operations: search long-term memory (openmemory.md or context).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_tool import BaseTool, ToolResult

DEFAULT_TOP_K = 5


def _resolve_openmemory_path() -> Optional[Path]:
    """Resolve path to openmemory.md (same logic as context memory adapter)."""
    path_env = os.getenv("OPENMEMORY_PATH")
    if path_env:
        p = Path(path_env)
        if p.is_file():
            return p
        candidate = p / "openmemory.md"
        if candidate.exists():
            return candidate
    cwd_file = Path(os.getcwd()) / "openmemory.md"
    if cwd_file.exists():
        return cwd_file
    start = Path(__file__).resolve().parent
    for parent in [start, *start.parents]:
        candidate = parent / "openmemory.md"
        if candidate.exists():
            return candidate
        if (parent / ".git").exists():
            root_candidate = parent / "openmemory.md"
            if root_candidate.exists():
                return root_candidate
            break
    return None


class SearchMemoryTool(BaseTool):
    """
    Search long-term memory (openmemory.md).

    Returns sections/lines that match the query (case-insensitive).
    Use for recalling project facts, patterns, and decisions.
    """

    name = "SearchMemory"
    description = "Search long-term memory (openmemory.md) by query; returns matching sections."
    required_params = ("query",)
    optional_params = {"top_k": DEFAULT_TOP_K}

    def execute(self, **params) -> ToolResult:
        """
        Search memory by query.

        Args:
            query: Search string (case-insensitive match in sections/lines)
            top_k: Max number of snippets to return (default 5)

        Returns:
            ToolResult with list of matching content snippets
        """
        query = (params.get("query") or "").strip()
        if not query:
            return ToolResult.fail("query is required")
        top_k = int(params.get("top_k", DEFAULT_TOP_K))
        path = _resolve_openmemory_path()
        if not path or not path.exists():
            return ToolResult.ok(output="No openmemory.md found; memory search returned nothing.")
        try:
            content = path.read_text(encoding="utf-8")
            lines = content.split("\n")
            query_lower = query.lower()
            current_section = ""
            matches: List[str] = []
            for line in lines:
                if line.startswith("## "):
                    current_section = line[3:].strip()
                if query_lower in line.lower() or query_lower in current_section.lower():
                    snippet = f"[{current_section}] {line.strip()}" if current_section else line.strip()
                    if snippet and snippet not in matches:
                        matches.append(snippet[:500])
                        if len(matches) >= top_k:
                            break
            output = "\n".join(matches) if matches else "No matching memory entries found."
            return ToolResult.ok(output=output, count=len(matches))
        except Exception as e:
            return ToolResult.fail(f"Memory search failed: {e}")
