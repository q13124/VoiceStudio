"""
VoiceStudio Skills Infrastructure.

Provides programmatic skill management, discovery, and registration.
"""

from tools.skills.registry import (
    SkillRegistry,
    Skill,
    SkillCategory,
    get_registry,
    list_skills,
    get_skill,
    register_skill,
)

__all__ = [
    "SkillRegistry",
    "Skill",
    "SkillCategory",
    "get_registry",
    "list_skills",
    "get_skill",
    "register_skill",
]
