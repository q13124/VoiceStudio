from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

from tools.context.core.models import AllocationContext, MemoryItem, SourceResult
from tools.context.sources.base import BaseSourceAdapter

logger = logging.getLogger(__name__)

# Project identifier for OpenMemory queries
PROJECT_ID = "wtsteward11/VoiceStudio"

# Memory types relevant for context injection
RELEVANT_MEMORY_TYPES = ["component", "implementation", "project_info", "debug"]

# Timeout for MCP operations (seconds)
_MCP_SEARCH_TIMEOUT = 15.0

# MCP server configurations
# OpenMemory (local HSG) uses openmemory_query
# Mem0 (cloud) uses search-memory
_MCP_TOOL_CONFIGS: dict[str, dict[str, Any]] = {
    "openmemory": {
        "command": "npx",
        "args": ["-y", "openmemory-mcp"],
        "tool_name": "openmemory_query",
        "param_mapping": {
            "query": "query",
            "max_results": "k",
            "query_type": "type",
        },
    },
    "mem0": {
        "command": "npx",
        "args": ["-y", "@mem0/mcp"],
        "tool_name": "search-memory",
        "param_mapping": {
            "query": "query",
            "max_results": "limit",
            "project_id": "project_id",
            "memory_types": "memory_types",
        },
    },
}


def _resolve_openmemory_path() -> str | None:
    """
    Resolve path to openmemory.md (OpenMemory canonical store).
    Order: OPENMEMORY_PATH env -> cwd -> repo root (walk up from this file).
    """
    path_env = os.getenv("OPENMEMORY_PATH")
    if path_env:
        p = Path(path_env)
        if p.is_file():
            return str(p)
        candidate = p / "openmemory.md"
        if candidate.exists():
            return str(candidate)
    cwd_file = Path(os.getcwd()) / "openmemory.md"
    if cwd_file.exists():
        return str(cwd_file)
    # Repo root: from this file, walk up to directory containing openmemory.md or .git
    start = Path(__file__).resolve().parent
    for parent in [start, *start.parents]:
        candidate = parent / "openmemory.md"
        if candidate.exists():
            return str(candidate)
        if (parent / ".git").exists():
            root_candidate = parent / "openmemory.md"
            if root_candidate.exists():
                return str(root_candidate)
            break
    return None


def _run_mcp_search(
    query: str,
    max_results: int,
    query_type: str = "contextual",
    provider: str = "openmemory",
) -> list[dict[str, Any]] | None:
    """
    Run memory search via MCP stdio client.

    Supports two providers:
    - "openmemory": Local HSG memory (openmemory_query tool)
    - "mem0": Cloud-based memory (search-memory tool)

    Returns None on any failure (caller falls back to file).
    """
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        logger.debug("mcp package not installed; skipping MCP memory search.")
        return None

    config = _MCP_TOOL_CONFIGS.get(provider)
    if not config:
        logger.debug("Unknown MCP provider: %s", provider)
        return None

    async def _search() -> list[dict[str, Any]] | None:
        env = os.environ.copy()
        # OpenMemory-specific environment
        if provider == "openmemory":
            env.setdefault("OM_TIER", "hybrid")
            env.setdefault("OM_EMBEDDINGS", "synthetic")

        params = StdioServerParameters(
            command=config["command"],
            args=config["args"],
            env=env,
        )

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Build tool arguments based on provider
                tool_args: dict[str, Any] = {}
                param_map = config["param_mapping"]

                if "query" in param_map:
                    tool_args[param_map["query"]] = query
                if "max_results" in param_map:
                    tool_args[param_map["max_results"]] = min(max_results, 32)
                if "query_type" in param_map:
                    tool_args[param_map["query_type"]] = query_type
                if "project_id" in param_map:
                    tool_args[param_map["project_id"]] = PROJECT_ID
                if "memory_types" in param_map:
                    tool_args[param_map["memory_types"]] = RELEVANT_MEMORY_TYPES

                tool_name = config["tool_name"]
                logger.debug("Calling MCP tool %s with args: %s", tool_name, tool_args)
                result = await session.call_tool(tool_name, tool_args)
                return _parse_mcp_tool_result(result, max_results)

    try:
        return asyncio.run(asyncio.wait_for(_search(), timeout=_MCP_SEARCH_TIMEOUT))
    except asyncio.TimeoutError:
        logger.debug("MCP search timed out after %s s (provider=%s)", _MCP_SEARCH_TIMEOUT, provider)
        return None
    except Exception as e:
        logger.debug("MCP search error (provider=%s): %s", provider, e)
        return None


def _try_all_mcp_providers(
    query: str,
    max_results: int,
    query_type: str = "contextual",
) -> list[dict[str, Any]] | None:
    """
    Try all configured MCP providers in order until one succeeds.
    Returns None if all providers fail.
    """
    for provider in _MCP_TOOL_CONFIGS:
        result = _run_mcp_search(query, max_results, query_type, provider)
        if result:
            logger.debug("MCP provider %s returned %d results", provider, len(result))
            return result
    return None


def _parse_mcp_tool_result(result: Any, max_results: int) -> list[dict[str, Any]] | None:
    """
    Parse MCP call_tool result into [{"content": str, "source": str, "relevance": float}].

    Handles multiple response formats:
    - OpenMemory HSG: {memories: [{content, sector, salience, ...}]}
    - Mem0: {results: [{memory: {content}, metadata: {source}}]}
    - Plain list: [{content, source}]
    - Raw text fallback

    Returns None if invalid/empty.
    """
    out: list[dict[str, Any]] = []
    raw_text = ""

    # Extract text content from MCP result blocks
    if hasattr(result, "content") and result.content:
        for block in result.content:
            if hasattr(block, "type") and block.type == "text" and hasattr(block, "text"):
                raw_text += block.text
            elif isinstance(block, dict):
                if block.get("type") == "text" and block.get("text"):
                    raw_text += block["text"]

    if not raw_text:
        return None

    # Try to parse as JSON
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        # Fallback: treat raw text as single memory
        out.append({"content": raw_text[:2000], "source": "openmemory", "relevance": 0.5})
        return out[:max_results]

    def _extract_memory(item: dict[str, Any]) -> dict[str, Any]:
        """Extract memory content from various item formats."""
        # Content extraction (try multiple fields)
        content = (
            item.get("content")
            or item.get("text")
            or (item.get("memory") or {}).get("content")
            or (item.get("memory") or {}).get("text")
        )
        if isinstance(content, dict):
            content = content.get("text") or content.get("content") or json.dumps(content)

        # Source extraction
        source = (
            item.get("source")
            or item.get("sector")  # OpenMemory HSG sector
            or (item.get("metadata") or {}).get("source")
            or "openmemory"
        )

        # Relevance/salience extraction
        relevance = (
            item.get("salience")  # OpenMemory HSG
            or item.get("relevance")
            or item.get("score")
            or item.get("similarity")
            or 0.5
        )

        return {
            "content": (str(content) if content else "")[:2000],
            "source": str(source),
            "relevance": float(relevance) if isinstance(relevance, (int, float)) else 0.5,
        }

    # Parse based on structure
    if isinstance(data, list):
        for item in data[:max_results]:
            if isinstance(item, dict):
                mem = _extract_memory(item)
                if mem["content"]:
                    out.append(mem)
            elif isinstance(item, str):
                out.append({"content": item[:2000], "source": "openmemory", "relevance": 0.5})
    elif isinstance(data, dict):
        # Try common wrapper keys
        items = (
            data.get("memories")
            or data.get("results")
            or data.get("data")
            or data.get("items")
            or []
        )

        if isinstance(items, list):
            for item in items[:max_results]:
                if isinstance(item, dict):
                    mem = _extract_memory(item)
                    if mem["content"]:
                        out.append(mem)

        # Fallback: top-level content
        if not out and "content" in data:
            out.append({
                "content": str(data["content"])[:2000],
                "source": data.get("source", "openmemory"),
                "relevance": data.get("salience", data.get("relevance", 0.5)),
            })

    return out[:max_results] if out else None


class MemorySourceAdapter(BaseSourceAdapter):
    """
    Fetch context from OpenMemory.

    Uses openmemory.md as the canonical local store (project SSOT).
    Optional: OPENMEMORY_PATH env points to file or directory containing openmemory.md.
    Falls back to CONTEXT_MEMO env if no file found.

    When mcp_enabled=True and offline=False, attempts OpenMemory MCP protocol
    (search-memory) first; on failure or when no MCP client is available,
    falls back to file/openmemory.md and logs once (ADR-015, option C).

    Features:
    - Role-aware memory retrieval based on role responsibilities
    - Task context injection for relevant memories
    - Health checking for memory sources availability
    """
    _mcp_unavailable_logged: bool = False

    # Role-specific memory query hints
    ROLE_QUERY_HINTS = {
        "overseer": ["project state", "milestones", "blockers", "governance"],
        "system-architect": ["architecture", "boundaries", "contracts", "ADRs"],
        "build-tooling": ["build", "CI/CD", "toolchain", "dependencies"],
        "ui-engineer": ["UI", "XAML", "MVVM", "views", "bindings"],
        "core-platform": ["runtime", "preflight", "storage", "jobs"],
        "engine-engineer": ["engines", "synthesis", "inference", "audio"],
        "release-engineer": ["installer", "packaging", "release", "versioning"],
        "debug-agent": ["errors", "exceptions", "debugging", "diagnostics"],
        "validator": ["verification", "proofs", "acceptance", "validation"],
    }

    def __init__(
        self,
        offline: bool = True,
        max_results: int = 5,
        query_type: str = "contextual",
        mcp_enabled: bool = False,
    ):
        super().__init__(source_name="memory", priority=50, offline=offline)
        self._max_results = max_results
        self._query_type = query_type
        self._mcp_enabled = mcp_enabled

    def health_check(self) -> bool:
        """Check if memory sources are available."""
        try:
            # Check for openmemory.md
            openmemory_path = _resolve_openmemory_path()
            if openmemory_path and os.path.exists(openmemory_path):
                return True

            # Check for CONTEXT_MEMO env
            if os.getenv("CONTEXT_MEMO"):
                return True

            # If MCP is enabled and not offline, consider it available
            return bool(self._mcp_enabled and not self._offline)
        except Exception as e:
            # GAP-PY-001: Best effort availability check
            logger.debug(f"Memory availability check failed: {e}")
            return False

    def _fetch_env_hint(self) -> list[MemoryItem]:
        """Fallback: read from CONTEXT_MEMO environment variable."""
        injected = os.getenv("CONTEXT_MEMO")
        if injected:
            return [MemoryItem(content=injected, source="env:CONTEXT_MEMO")]
        return []

    def _try_openmemory_mcp_protocol(
        self, query: str, max_results: int
    ) -> list[dict[str, Any]] | None:
        """
        Attempt OpenMemory MCP protocol via stdio client.

        Tries configured MCP providers (openmemory, mem0) in order:
        1. openmemory: Local HSG memory (openmemory_query tool)
        2. mem0: Cloud-based memory (search-memory tool)

        Returns None if no MCP client is available or all calls fail (fallback to file).
        """
        try:
            return _try_all_mcp_providers(
                query=query,
                max_results=max_results,
                query_type=self._query_type,
            )
        except Exception as e:
            logger.debug("OpenMemory MCP search failed: %s", e)
            return None

    def _call_openmemory_mcp(
        self, query: str, max_results: int = 5
    ) -> list[dict[str, Any]] | None:
        """
        Call OpenMemory MCP when mcp_enabled; else or on failure use file fallback.
        MCP unavailable -> log once, continue with file (openmemory.mdc).
        """
        if self._mcp_enabled and not self._offline:
            result = self._try_openmemory_mcp_protocol(query, max_results)
            if result and isinstance(result, list):
                return result
            if not MemorySourceAdapter._mcp_unavailable_logged:
                logger.warning(
                    "OpenMemory MCP not available; using file fallback (openmemory.md). "
                    "Set memory.mcp_enabled=false or wire an MCP client in _try_openmemory_mcp_protocol."
                )
                MemorySourceAdapter._mcp_unavailable_logged = True
        return self._try_mcp_query({"query": query, "k": min(max_results, 32)})

    def _try_mcp_query(self, args: dict[str, Any]) -> list[dict[str, Any]] | None:
        """
        Query OpenMemory local store (openmemory.md).

        Uses _resolve_openmemory_path() for cwd, OPENMEMORY_PATH, or repo root.
        MCP protocol integration can be added when an MCP client is available.
        """
        openmemory_path = _resolve_openmemory_path()
        if openmemory_path and os.path.exists(openmemory_path):
            try:
                with open(openmemory_path, encoding="utf-8") as f:
                    content = f.read()

                # Extract relevant sections based on query
                query = args.get("query", "").lower()
                memories = []

                # Parse sections from openmemory.md
                sections = self._parse_openmemory_sections(content)

                for section_name, section_content in sections.items():
                    # Simple relevance matching
                    if query and query in section_name.lower():
                        memories.append({
                            "content": section_content[:500],  # Truncate for budget
                            "source": f"openmemory:{section_name}",
                            "relevance": 0.8,
                        })
                    elif not query:
                        # No query - return overview sections
                        if section_name.lower() in ["overview", "architecture", "components"]:
                            memories.append({
                                "content": section_content[:500],
                                "source": f"openmemory:{section_name}",
                                "relevance": 0.5,
                            })

                return memories[:args.get("k", 5)]

            except Exception as e:
                logger.debug(f"Failed to read openmemory.md: {e}")

        return None

    def _parse_openmemory_sections(self, content: str) -> dict[str, str]:
        """Parse openmemory.md into named sections."""
        sections = {}
        current_section = "root"
        current_content: list[str] = []

        for line in content.split("\n"):
            if line.startswith("## "):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content)

        return sections

    def _build_query(self, context: AllocationContext) -> str:
        """Build role-aware search query from allocation context."""
        parts = []

        if context.task_id:
            parts.append(f"task:{context.task_id}")

        if context.phase:
            parts.append(f"phase:{context.phase}")

        # Add role-specific query hints
        if context.role:
            parts.append(f"role:{context.role}")
            hints = self.ROLE_QUERY_HINTS.get(context.role, [])
            if hints:
                # Add top 2 role hints to improve relevance
                parts.extend(hints[:2])

        if not parts:
            parts.append("VoiceStudio project context")

        return " ".join(parts)

    def _get_role_relevant_sections(
        self,
        sections: dict[str, str],
        role: str | None,
    ) -> list[dict[str, Any]]:
        """Filter sections relevant to a specific role."""
        if not role:
            return []

        hints = self.ROLE_QUERY_HINTS.get(role, [])
        if not hints:
            return []

        relevant = []
        for section_name, content in sections.items():
            # Check if section matches role hints
            section_lower = section_name.lower()
            for hint in hints:
                if hint.lower() in section_lower or hint.lower() in content.lower()[:200]:
                    relevant.append({
                        "content": content[:500],
                        "source": f"openmemory:{section_name}",
                        "relevance": 0.85,
                    })
                    break  # Only add once per section

        return relevant[:self._max_results]

    def _convert_to_memory_items(
        self, memories: list[dict[str, Any]]
    ) -> list[MemoryItem]:
        """Convert MCP response to MemoryItem list."""
        items = []
        for mem in memories:
            content = mem.get("content", "")
            source = mem.get("source", "openmemory")

            if content:
                items.append(MemoryItem(content=content, source=source))

        return items

    def fetch(self, context: AllocationContext) -> SourceResult:
        """
        Fetch memories from OpenMemory with role-aware retrieval.

        Priority:
        1. OpenMemory MCP query (if available and not offline)
        2. Local openmemory.md file with role-aware section filtering
        3. Query-based local search
        4. CONTEXT_MEMO environment variable
        """
        def _load():
            all_memories = []

            # Try OpenMemory MCP integration
            if not self._offline:
                query = self._build_query(context)
                mcp_memories = self._call_openmemory_mcp(query, self._max_results)

                if mcp_memories:
                    items = self._convert_to_memory_items(mcp_memories)
                    if items:
                        all_memories.extend(items)

            # Try role-aware local retrieval
            openmemory_path = _resolve_openmemory_path()
            if openmemory_path and os.path.exists(openmemory_path):
                try:
                    with open(openmemory_path, encoding="utf-8") as f:
                        content = f.read()

                    sections = self._parse_openmemory_sections(content)

                    # Get role-relevant sections first
                    if context.role:
                        role_memories = self._get_role_relevant_sections(
                            sections, context.role
                        )
                        items = self._convert_to_memory_items(role_memories)
                        all_memories.extend(items)

                    # If still under limit, add query-matched sections
                    if len(all_memories) < self._max_results:
                        query = self._build_query(context)
                        query_memories = self._try_mcp_query({
                            "query": query,
                            "k": self._max_results - len(all_memories),
                        })
                        if query_memories:
                            items = self._convert_to_memory_items(query_memories)
                            # Avoid duplicates
                            existing_contents = {m.content[:100] for m in all_memories}
                            for item in items:
                                if item.content[:100] not in existing_contents:
                                    all_memories.append(item)

                except Exception as e:
                    logger.debug("Failed to read openmemory.md: %s", e)

            # Final fallback: environment variable
            if not all_memories:
                all_memories = self._fetch_env_hint()

            return {"memory": all_memories[:self._max_results]}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        """Estimate memory context size."""
        mem = self._fetch_env_hint()
        if not mem:
            return 0
        return sum(len(m.content) for m in mem)

    def store_memory(
        self,
        content: str,
        title: str,
        memory_type: str = "project_info",
        section: str | None = None,
    ) -> bool:
        """
        Store a memory to the local openmemory.md file.

        Args:
            content: Memory content to store
            title: Memory title
            memory_type: Type of memory (component, implementation, debug, etc.)
            section: Optional section to add to in openmemory.md

        Returns:
            True if stored successfully
        """
        openmemory_path = _resolve_openmemory_path()
        if not openmemory_path:
            # Create in cwd if not exists
            openmemory_path = str(Path(os.getcwd()) / "openmemory.md")

        try:
            path = Path(openmemory_path)

            # Read existing content or create template
            if path.exists():
                existing = path.read_text(encoding="utf-8")
            else:
                existing = self._create_openmemory_template()

            # Format the new memory entry
            timestamp = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
            entry = f"\n### {title}\n- Type: {memory_type}\n- Added: {timestamp}\n\n{content}\n"

            # Find the right section to add to
            target_section = section or self._memory_type_to_section(memory_type)
            updated = self._insert_memory_entry(existing, entry, target_section)

            path.write_text(updated, encoding="utf-8")
            logger.info("Stored memory: %s (type: %s)", title, memory_type)
            return True

        except Exception as e:
            logger.error("Failed to store memory: %s", e)
            return False

    def _create_openmemory_template(self) -> str:
        """Create a new openmemory.md template."""
        return """# VoiceStudio OpenMemory

## Overview
Project knowledge and accumulated context.

## Architecture
System architecture and design decisions.

## Components
Major components and their responsibilities.

## Patterns
Coding patterns and conventions.

## Debug History
Notable debugging sessions and solutions.

## User Defined Namespaces
- [Leave blank - user populates]
"""

    def _memory_type_to_section(self, memory_type: str) -> str:
        """Map memory type to openmemory.md section."""
        mapping = {
            "component": "Components",
            "implementation": "Patterns",
            "debug": "Debug History",
            "project_info": "Overview",
            "user_preference": "User Defined Namespaces",
        }
        return mapping.get(memory_type, "Overview")

    def _insert_memory_entry(
        self,
        content: str,
        entry: str,
        section: str,
    ) -> str:
        """Insert a memory entry into the appropriate section."""
        lines = content.split("\n")
        result = []
        in_section = False
        entry_added = False

        for _i, line in enumerate(lines):
            result.append(line)

            # Check if we're entering the target section
            if line.startswith("## ") and section.lower() in line.lower():
                in_section = True
                continue

            # Check if we're leaving a section
            if in_section and line.startswith("## "):
                if not entry_added:
                    result.insert(len(result) - 1, entry)
                    entry_added = True
                in_section = False

        # If section was at the end, add entry
        if in_section and not entry_added:
            result.append(entry)

        # If section not found, add at end
        if not entry_added:
            result.append(f"\n## {section}")
            result.append(entry)

        return "\n".join(result)
