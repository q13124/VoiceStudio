"""
Task Classifier for VoiceStudio.

Classifies user prompts into role profiles based on keyword matching
and file pattern hints. Used by the MCP auto-selection system.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of task classification."""
    
    role_profile: str  # e.g., "build-tooling", "ui-engineer"
    role_id: int  # Numeric role ID (0-7)
    display_name: str  # Human-readable name
    task_type: str  # e.g., "build", "ui", "engine", "debug"
    confidence: float  # 0.0 to 1.0
    keywords_matched: List[str] = field(default_factory=list)
    file_patterns_matched: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role_profile": self.role_profile,
            "role_id": self.role_id,
            "display_name": self.display_name,
            "task_type": self.task_type,
            "confidence": self.confidence,
            "keywords_matched": self.keywords_matched,
            "file_patterns_matched": self.file_patterns_matched,
        }


@dataclass
class RoleConfig:
    """Configuration for a role."""
    
    id: int
    display_name: str
    keywords: List[str]
    file_patterns: List[str]
    weight: float = 1.0


class TaskClassifier:
    """
    Keyword-based task classification with optional file hints.
    
    Classifies user prompts into VoiceStudio role profiles for
    context routing and MCP auto-selection.
    
    Features:
    - Keyword matching with weights
    - File extension/path pattern hints
    - Configurable confidence thresholds
    - Multi-match ranking
    """
    
    # Default path to keywords configuration
    DEFAULT_KEYWORDS_PATH = "tools/context/config/task_keywords.json"
    
    def __init__(
        self,
        keywords_path: Optional[str] = None,
        auto_select_threshold: float = 0.6,
        suggest_threshold: float = 0.4,
    ):
        """
        Initialize task classifier.
        
        Args:
            keywords_path: Path to keywords configuration file.
            auto_select_threshold: Confidence threshold for auto-selection.
            suggest_threshold: Confidence threshold for suggestions.
        """
        self._keywords_path = keywords_path or self.DEFAULT_KEYWORDS_PATH
        self._auto_select_threshold = auto_select_threshold
        self._suggest_threshold = suggest_threshold
        
        # Load configuration
        self._roles: Dict[str, RoleConfig] = {}
        self._thresholds: Dict[str, float] = {}
        self._boosters: Dict[str, float] = {}
        self._load_config()
        
        logger.info(
            "TaskClassifier initialized with %d roles",
            len(self._roles),
        )
    
    def _load_config(self) -> None:
        """Load keywords configuration from file."""
        config_path = Path(self._keywords_path)
        
        if not config_path.exists():
            logger.warning(
                "Keywords config not found at %s, using defaults",
                config_path,
            )
            self._load_defaults()
            return
        
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            
            # Load roles
            for role_name, role_data in config.get("roles", {}).items():
                self._roles[role_name] = RoleConfig(
                    id=role_data.get("id", 0),
                    display_name=role_data.get("display_name", role_name),
                    keywords=[k.lower() for k in role_data.get("keywords", [])],
                    file_patterns=role_data.get("file_patterns", []),
                    weight=role_data.get("weight", 1.0),
                )
            
            # Load thresholds
            self._thresholds = config.get("confidence_thresholds", {
                "auto_select": 0.6,
                "suggest": 0.4,
                "min_match": 0.2,
            })
            
            # Load boosters
            self._boosters = config.get("boosters", {
                "file_pattern_match": 0.2,
                "multiple_keywords": 0.1,
                "exact_match": 0.15,
            })
            
            logger.info("Loaded %d roles from config", len(self._roles))
            
        except Exception as e:
            logger.error("Failed to load config: %s", e)
            self._load_defaults()
    
    def _load_defaults(self) -> None:
        """Load default role configurations."""
        self._roles = {
            "build-tooling": RoleConfig(
                id=2,
                display_name="Build & Tooling",
                keywords=["build", "compile", "ci", "pipeline", "msbuild", "dotnet"],
                file_patterns=["*.csproj", "*.sln", ".github/workflows/*"],
            ),
            "ui-engineer": RoleConfig(
                id=3,
                display_name="UI Engineer",
                keywords=["xaml", "ui", "panel", "view", "button", "binding", "winui"],
                file_patterns=["*.xaml", "*ViewModel.cs"],
            ),
            "engine-engineer": RoleConfig(
                id=5,
                display_name="Engine Engineer",
                keywords=["engine", "tts", "synthesis", "model", "inference", "cuda"],
                file_patterns=["*_engine.py", "engines/*"],
            ),
            "debug-agent": RoleConfig(
                id=7,
                display_name="Debug Agent",
                keywords=["debug", "error", "exception", "crash", "bug", "fix"],
                file_patterns=["*.log"],
            ),
        }
        
        self._thresholds = {
            "auto_select": 0.6,
            "suggest": 0.4,
            "min_match": 0.2,
        }
        
        self._boosters = {
            "file_pattern_match": 0.2,
            "multiple_keywords": 0.1,
            "exact_match": 0.15,
        }
    
    def classify(
        self,
        prompt: str,
        file_hint: Optional[str] = None,
    ) -> ClassificationResult:
        """
        Classify a user prompt into a role profile.
        
        Args:
            prompt: The user's task prompt.
            file_hint: Optional file path hint for context.
            
        Returns:
            ClassificationResult with role and confidence.
        """
        prompt_lower = prompt.lower()
        
        # Score each role
        scores: List[Tuple[str, float, List[str], List[str]]] = []
        
        for role_name, role_config in self._roles.items():
            score, matched_keywords, matched_patterns = self._score_role(
                prompt_lower,
                file_hint,
                role_config,
            )
            
            if score > 0:
                scores.append((role_name, score, matched_keywords, matched_patterns))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        if not scores:
            # No matches - default to debug-agent
            return ClassificationResult(
                role_profile="debug-agent",
                role_id=7,
                display_name="Debug Agent",
                task_type="unknown",
                confidence=0.0,
                keywords_matched=[],
                file_patterns_matched=[],
            )
        
        # Get best match
        best_role, best_score, best_keywords, best_patterns = scores[0]
        role_config = self._roles[best_role]
        
        # Normalize confidence to 0-1
        max_possible_score = len(role_config.keywords) + 3.0  # Rough max
        confidence = min(best_score / max_possible_score, 1.0)
        
        # Determine task type from role name
        task_type = self._role_to_task_type(best_role)
        
        return ClassificationResult(
            role_profile=best_role,
            role_id=role_config.id,
            display_name=role_config.display_name,
            task_type=task_type,
            confidence=confidence,
            keywords_matched=best_keywords,
            file_patterns_matched=best_patterns,
        )
    
    def _score_role(
        self,
        prompt_lower: str,
        file_hint: Optional[str],
        role_config: RoleConfig,
    ) -> Tuple[float, List[str], List[str]]:
        """
        Score how well a prompt matches a role.
        
        Returns:
            Tuple of (score, matched_keywords, matched_patterns).
        """
        score = 0.0
        matched_keywords: List[str] = []
        matched_patterns: List[str] = []
        
        # Keyword matching
        for keyword in role_config.keywords:
            if keyword in prompt_lower:
                score += role_config.weight
                matched_keywords.append(keyword)
                
                # Bonus for exact word match (not substring)
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, prompt_lower):
                    score += self._boosters.get("exact_match", 0.15)
        
        # Multiple keywords bonus
        if len(matched_keywords) >= 3:
            score += self._boosters.get("multiple_keywords", 0.1) * len(matched_keywords)
        
        # File pattern matching
        if file_hint:
            file_hint_lower = file_hint.lower()
            for pattern in role_config.file_patterns:
                if self._match_file_pattern(file_hint_lower, pattern.lower()):
                    score += self._boosters.get("file_pattern_match", 0.2)
                    matched_patterns.append(pattern)
        
        return score, matched_keywords, matched_patterns
    
    def _match_file_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if a file path matches a pattern."""
        # Simple glob-like matching
        if pattern.startswith("*"):
            return file_path.endswith(pattern[1:])
        if pattern.endswith("*"):
            return file_path.startswith(pattern[:-1])
        if "*" in pattern:
            parts = pattern.split("*")
            return all(part in file_path for part in parts if part)
        return pattern in file_path
    
    def _role_to_task_type(self, role_name: str) -> str:
        """Map role name to task type."""
        mapping = {
            "overseer": "governance",
            "system-architect": "architecture",
            "build-tooling": "build",
            "ui-engineer": "ui",
            "core-platform": "backend",
            "engine-engineer": "engine",
            "release-engineer": "release",
            "debug-agent": "debug",
        }
        return mapping.get(role_name, "unknown")
    
    def classify_batch(
        self,
        prompts: List[str],
        file_hints: Optional[List[str]] = None,
    ) -> List[ClassificationResult]:
        """
        Classify multiple prompts.
        
        Args:
            prompts: List of user prompts.
            file_hints: Optional list of file hints (same length as prompts).
            
        Returns:
            List of ClassificationResults.
        """
        if file_hints and len(file_hints) != len(prompts):
            raise ValueError("file_hints must match prompts length")
        
        results = []
        for i, prompt in enumerate(prompts):
            hint = file_hints[i] if file_hints else None
            results.append(self.classify(prompt, hint))
        
        return results
    
    def should_auto_select(self, result: ClassificationResult) -> bool:
        """Check if result confidence is high enough for auto-selection."""
        return result.confidence >= self._auto_select_threshold
    
    def should_suggest(self, result: ClassificationResult) -> bool:
        """Check if result confidence is high enough for suggestion."""
        return result.confidence >= self._suggest_threshold
    
    def get_all_roles(self) -> Dict[str, RoleConfig]:
        """Get all configured roles."""
        return self._roles.copy()
    
    def get_role_by_id(self, role_id: int) -> Optional[str]:
        """Get role name by ID."""
        for role_name, config in self._roles.items():
            if config.id == role_id:
                return role_name
        return None


# Module-level convenience function
_classifier: Optional[TaskClassifier] = None


def get_classifier() -> TaskClassifier:
    """Get or create global TaskClassifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = TaskClassifier()
    return _classifier
