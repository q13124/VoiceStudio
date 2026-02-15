"""
VoiceStudio Skills Infrastructure.

Provides programmatic skill management, discovery, and registration.
"""

from tools.skills.registry import (
    Skill,
    SkillCategory,
    SkillRegistry,
    get_registry,
    get_skill,
    list_skills,
    register_skill,
)

__all__ = [
    "Skill",
    "SkillCategory",
    "SkillRegistry",
    "get_registry",
    "get_skill",
    "list_skills",
    "register_skill",
]
