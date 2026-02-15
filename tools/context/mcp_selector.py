"""
MCP Selector for VoiceStudio.

Selects appropriate MCP (Model Context Protocol) servers based on
task classification, role profile, and keyword analysis.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.context.classifier.task_classifier import ClassificationResult

logger = logging.getLogger(__name__)


@dataclass
class MCPRecommendation:
    """Recommendation of MCPs for a task."""

    mcps: list[str]  # Ordered list of recommended MCPs
    role_mcps: list[str]  # MCPs from role mapping
    keyword_mcps: list[str]  # MCPs from keyword matching
    always_available: list[str]  # MCPs always included
    confidence: float  # Overall recommendation confidence
    reasoning: str  # Human-readable reasoning

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "mcps": self.mcps,
            "role_mcps": self.role_mcps,
            "keyword_mcps": self.keyword_mcps,
            "always_available": self.always_available,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
        }

    def to_preamble(self) -> str:
        """Format as context preamble for prompt injection."""
        if not self.mcps:
            return ""

        lines = ["## Recommended MCP Servers", ""]
        lines.append(f"Based on task analysis (confidence: {self.confidence:.0%}), consider using:")
        lines.append("")
        for mcp in self.mcps:
            lines.append(f"- `{mcp}`")
        lines.append("")
        lines.append(f"*{self.reasoning}*")
        return "\n".join(lines)


class MCPSelector:
    """
    Selects MCP servers based on task classification and keywords.

    Uses role-to-MCP mappings and keyword-to-MCP mappings to recommend
    appropriate MCP servers for a given task.

    Features:
    - Role-based MCP recommendations
    - Keyword-based MCP recommendations
    - Priority ordering for multiple matches
    - Maximum MCP limit per request
    - Always-available MCP inclusion
    """

    DEFAULT_ROUTING_PATH = "tools/context/config/mcp_routing.json"

    def __init__(
        self,
        routing_path: str | None = None,
        max_mcps: int = 5,
    ):
        """
        Initialize MCP selector.

        Args:
            routing_path: Path to MCP routing configuration.
            max_mcps: Maximum MCPs to recommend per request.
        """
        self._routing_path = routing_path or self.DEFAULT_ROUTING_PATH
        self._max_mcps = max_mcps

        # Load configuration
        self._role_to_mcps: dict[str, list[str]] = {}
        self._keyword_to_mcps: dict[str, list[str]] = {}
        self._always_available: list[str] = []
        self._priority_order: list[str] = []
        self._descriptions: dict[str, str] = {}

        self._load_config()

        logger.info(
            "MCPSelector initialized with %d role mappings, %d keyword mappings",
            len(self._role_to_mcps),
            len(self._keyword_to_mcps),
        )

    def _load_config(self) -> None:
        """Load MCP routing configuration."""
        config_path = Path(self._routing_path)

        if not config_path.exists():
            logger.warning(
                "MCP routing config not found at %s, using defaults",
                config_path,
            )
            self._load_defaults()
            return

        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))

            self._role_to_mcps = config.get("role_to_mcps", {})
            self._keyword_to_mcps = config.get("keyword_to_mcps", {})
            self._always_available = config.get("always_available", [])
            self._priority_order = config.get("priority_order", {}).get("order", [])
            self._max_mcps = config.get("max_mcps_per_request", self._max_mcps)
            self._descriptions = config.get("mcp_descriptions", {})

            logger.info("Loaded MCP routing config")

        except Exception as e:
            logger.error("Failed to load MCP routing config: %s", e)
            self._load_defaults()

    def _load_defaults(self) -> None:
        """Load default MCP routing configuration."""
        self._role_to_mcps = {
            "build-tooling": ["docker-mcp", "semgrep", "git"],
            "ui-engineer": ["playwright"],
            "engine-engineer": ["chroma", "context7"],
            "debug-agent": ["git", "semgrep"],
        }

        self._keyword_to_mcps = {
            "api": ["openapi-explorer", "context7"],
            "test": ["playwright"],
            "security": ["semgrep"],
        }

        self._always_available = ["git", "openmemory"]
        self._priority_order = ["git", "openmemory", "semgrep", "context7"]

    def recommend(
        self,
        prompt: str,
        role_profile: str | None = None,
        classification: ClassificationResult | None = None,
    ) -> MCPRecommendation:
        """
        Recommend MCPs for a task.

        Args:
            prompt: The user's task prompt.
            role_profile: Optional role profile (e.g., "build-tooling").
            classification: Optional ClassificationResult from TaskClassifier.

        Returns:
            MCPRecommendation with ordered list of MCPs.
        """
        prompt_lower = prompt.lower()

        # Collect MCPs from all sources
        role_mcps: set[str] = set()
        keyword_mcps: set[str] = set()

        # Get role from classification if not provided
        if classification and not role_profile:
            role_profile = classification.role_profile

        # Role-based MCPs
        if role_profile and role_profile in self._role_to_mcps:
            role_mcps.update(self._role_to_mcps[role_profile])

        # Keyword-based MCPs
        for keyword, mcps in self._keyword_to_mcps.items():
            if keyword in prompt_lower:
                keyword_mcps.update(mcps)

        # Combine all MCPs
        all_mcps: set[str] = set()
        all_mcps.update(self._always_available)
        all_mcps.update(role_mcps)
        all_mcps.update(keyword_mcps)

        # Sort by priority
        sorted_mcps = self._sort_by_priority(list(all_mcps))

        # Limit to max
        final_mcps = sorted_mcps[:self._max_mcps]

        # Build reasoning
        reasoning_parts = []
        if role_profile:
            reasoning_parts.append(f"Role: {role_profile}")
        if keyword_mcps:
            reasoning_parts.append(f"Keywords matched: {', '.join(sorted(keyword_mcps)[:3])}")
        if not reasoning_parts:
            reasoning_parts.append("Using default MCPs")

        reasoning = " | ".join(reasoning_parts)

        # Calculate confidence
        confidence = 0.5  # Base confidence
        if role_mcps:
            confidence += 0.2
        if keyword_mcps:
            confidence += 0.2
        if classification and classification.confidence > 0.5:
            confidence += 0.1
        confidence = min(confidence, 1.0)

        return MCPRecommendation(
            mcps=final_mcps,
            role_mcps=list(role_mcps),
            keyword_mcps=list(keyword_mcps),
            always_available=self._always_available.copy(),
            confidence=confidence,
            reasoning=reasoning,
        )

    def _sort_by_priority(self, mcps: list[str]) -> list[str]:
        """Sort MCPs by priority order."""
        def priority_key(mcp: str) -> int:
            try:
                return self._priority_order.index(mcp)
            except ValueError:
                return len(self._priority_order)  # Put unknown at end

        return sorted(mcps, key=priority_key)

    def get_role_mcps(self, role_profile: str) -> list[str]:
        """Get MCPs for a specific role."""
        return self._role_to_mcps.get(role_profile, []).copy()

    def get_keyword_mcps(self, keyword: str) -> list[str]:
        """Get MCPs for a specific keyword."""
        return self._keyword_to_mcps.get(keyword.lower(), []).copy()

    def get_all_mcps(self) -> set[str]:
        """Get all known MCP names."""
        all_mcps: set[str] = set()
        all_mcps.update(self._always_available)
        for mcps in self._role_to_mcps.values():
            all_mcps.update(mcps)
        for mcps in self._keyword_to_mcps.values():
            all_mcps.update(mcps)
        return all_mcps

    def get_mcp_description(self, mcp: str) -> str | None:
        """Get description for an MCP."""
        return self._descriptions.get(mcp)


# Module-level convenience functions
_selector: MCPSelector | None = None


def get_mcp_selector() -> MCPSelector:
    """Get or create global MCPSelector instance."""
    global _selector
    if _selector is None:
        _selector = MCPSelector()
    return _selector


def recommend_mcps(
    prompt: str | None = None,
    role_profile: str | None = None,
) -> list[str]:
    """
    Convenience function to recommend MCPs for a task.

    This is the primary entry point used by inject_context.py.

    Args:
        prompt: Optional user prompt text.
        role_profile: Optional role profile (e.g., "build-tooling").

    Returns:
        List of recommended MCP server names.
    """
    selector = get_mcp_selector()

    recommendation = selector.recommend(
        prompt=prompt or "",
        role_profile=role_profile,
    )

    return recommendation.mcps
