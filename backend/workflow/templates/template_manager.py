"""
Phase 6: Template System
Task 6.8: Project and workflow templates.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TemplateCategory(Enum):
    """Template categories."""
    PROJECT = "project"
    WORKFLOW = "workflow"
    VOICE = "voice"
    SYNTHESIS = "synthesis"
    EXPORT = "export"
    CUSTOM = "custom"


@dataclass
class TemplateVariable:
    """A variable in a template."""
    name: str
    description: str
    type: str  # string, number, boolean, path, choice
    default: Any = None
    required: bool = True
    choices: list[Any] = field(default_factory=list)
    validation: str | None = None  # regex pattern


@dataclass
class Template:
    """A template definition."""
    id: str
    name: str
    description: str
    category: TemplateCategory
    version: str = "1.0"
    author: str = ""
    tags: list[str] = field(default_factory=list)
    variables: list[TemplateVariable] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)  # path -> content
    created_at: datetime = field(default_factory=datetime.now)
    is_builtin: bool = False


@dataclass
class InstantiatedTemplate:
    """Result of instantiating a template."""
    success: bool
    output_path: Path | None = None
    files_created: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class TemplateManager:
    """Manager for project and workflow templates."""

    def __init__(self, templates_dir: Path | None = None):
        self._templates_dir = templates_dir or Path.home() / ".voicestudio/templates"
        self._templates_dir.mkdir(parents=True, exist_ok=True)
        self._templates: dict[str, Template] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load templates from disk and built-ins."""
        # Load built-in templates
        self._load_builtin_templates()

        # Load user templates
        for template_file in self._templates_dir.glob("*.json"):
            try:
                data = json.loads(template_file.read_text(encoding='utf-8'))
                template = self._parse_template(data)
                self._templates[template.id] = template
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")

    def _load_builtin_templates(self) -> None:
        """Load built-in templates."""
        # Basic project template
        self._templates["basic_project"] = Template(
            id="basic_project",
            name="Basic Project",
            description="A simple project with one audio track",
            category=TemplateCategory.PROJECT,
            author="VoiceStudio",
            is_builtin=True,
            variables=[
                TemplateVariable(
                    name="project_name",
                    description="Name of the project",
                    type="string",
                    default="New Project",
                ),
            ],
            files={
                "project.json": json.dumps({
                    "name": "{{project_name}}",
                    "version": "1.0",
                    "tracks": [
                        {"name": "Main", "type": "audio"}
                    ],
                }, indent=2),
                "README.md": "# {{project_name}}\n\nVoiceStudio project.\n",
            },
        )

        # Podcast template
        self._templates["podcast_project"] = Template(
            id="podcast_project",
            name="Podcast Project",
            description="Project optimized for podcast production",
            category=TemplateCategory.PROJECT,
            author="VoiceStudio",
            is_builtin=True,
            tags=["podcast", "voice", "production"],
            variables=[
                TemplateVariable(
                    name="project_name",
                    description="Podcast name",
                    type="string",
                    default="My Podcast",
                ),
                TemplateVariable(
                    name="episode_number",
                    description="Episode number",
                    type="number",
                    default=1,
                ),
            ],
            files={
                "project.json": json.dumps({
                    "name": "{{project_name}} - Episode {{episode_number}}",
                    "type": "podcast",
                    "tracks": [
                        {"name": "Host", "type": "voice"},
                        {"name": "Guest", "type": "voice"},
                        {"name": "Music", "type": "audio"},
                        {"name": "SFX", "type": "audio"},
                    ],
                }, indent=2),
                "assets/.gitkeep": "",
                "exports/.gitkeep": "",
            },
        )

        # Audiobook template
        self._templates["audiobook_project"] = Template(
            id="audiobook_project",
            name="Audiobook Project",
            description="Project for audiobook production with chapters",
            category=TemplateCategory.PROJECT,
            author="VoiceStudio",
            is_builtin=True,
            tags=["audiobook", "voice", "chapters"],
            variables=[
                TemplateVariable(
                    name="book_title",
                    description="Book title",
                    type="string",
                    default="My Audiobook",
                ),
                TemplateVariable(
                    name="author_name",
                    description="Author name",
                    type="string",
                    default="Author",
                ),
                TemplateVariable(
                    name="num_chapters",
                    description="Number of chapters",
                    type="number",
                    default=10,
                ),
            ],
            files={
                "project.json": json.dumps({
                    "name": "{{book_title}}",
                    "author": "{{author_name}}",
                    "type": "audiobook",
                    "chapters": "{{num_chapters}}",
                }, indent=2),
                "chapters/.gitkeep": "",
                "voices/.gitkeep": "",
            },
        )

        # Batch synthesis workflow
        self._templates["batch_synthesis_workflow"] = Template(
            id="batch_synthesis_workflow",
            name="Batch Synthesis Workflow",
            description="Workflow for processing multiple texts",
            category=TemplateCategory.WORKFLOW,
            author="VoiceStudio",
            is_builtin=True,
            variables=[
                TemplateVariable(
                    name="voice",
                    description="Voice to use",
                    type="string",
                    default="default",
                ),
                TemplateVariable(
                    name="output_format",
                    description="Output audio format",
                    type="choice",
                    choices=["wav", "mp3", "flac"],
                    default="wav",
                ),
            ],
            files={
                "workflow.json": json.dumps({
                    "name": "Batch Synthesis",
                    "steps": [
                        {
                            "type": "synthesize",
                            "config": {"voice": "{{voice}}"},
                        },
                        {
                            "type": "export",
                            "config": {"format": "{{output_format}}"},
                        },
                    ],
                }, indent=2),
            },
        )

    def _parse_template(self, data: dict[str, Any]) -> Template:
        """Parse a template from dictionary."""
        variables = [
            TemplateVariable(
                name=v["name"],
                description=v.get("description", ""),
                type=v.get("type", "string"),
                default=v.get("default"),
                required=v.get("required", True),
                choices=v.get("choices", []),
                validation=v.get("validation"),
            )
            for v in data.get("variables", [])
        ]

        return Template(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            category=TemplateCategory(data.get("category", "custom")),
            version=data.get("version", "1.0"),
            author=data.get("author", ""),
            tags=data.get("tags", []),
            variables=variables,
            files=data.get("files", {}),
            is_builtin=data.get("is_builtin", False),
        )

    def get_template(self, template_id: str) -> Template | None:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def list_templates(
        self,
        category: TemplateCategory | None = None
    ) -> list[Template]:
        """List available templates."""
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        return templates

    def instantiate(
        self,
        template_id: str,
        output_path: Path,
        variables: dict[str, Any]
    ) -> InstantiatedTemplate:
        """Instantiate a template with variables."""
        template = self._templates.get(template_id)
        if not template:
            return InstantiatedTemplate(
                success=False,
                errors=[f"Template not found: {template_id}"]
            )

        result = InstantiatedTemplate(success=True)

        try:
            # Validate required variables
            for var in template.variables:
                if var.required and var.name not in variables:
                    if var.default is not None:
                        variables[var.name] = var.default
                    else:
                        result.errors.append(f"Missing required variable: {var.name}")

            if result.errors:
                result.success = False
                return result

            # Create output directory
            output_path.mkdir(parents=True, exist_ok=True)

            # Process files
            for file_path, content in template.files.items():
                # Replace variables in path
                processed_path = self._replace_variables(file_path, variables)

                # Replace variables in content
                processed_content = self._replace_variables(content, variables)

                # Write file
                full_path = output_path / processed_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(processed_content, encoding='utf-8')

                result.files_created.append(str(full_path))

            result.output_path = output_path

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _replace_variables(self, text: str, variables: dict[str, Any]) -> str:
        """Replace {{variable}} placeholders in text."""
        for name, value in variables.items():
            placeholder = "{{" + name + "}}"
            text = text.replace(placeholder, str(value))

        return text

    def save_template(self, template: Template) -> bool:
        """Save a template to disk."""
        try:
            data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category.value,
                "version": template.version,
                "author": template.author,
                "tags": template.tags,
                "variables": [
                    {
                        "name": v.name,
                        "description": v.description,
                        "type": v.type,
                        "default": v.default,
                        "required": v.required,
                        "choices": v.choices,
                        "validation": v.validation,
                    }
                    for v in template.variables
                ],
                "files": template.files,
            }

            path = self._templates_dir / f"{template.id}.json"
            path.write_text(json.dumps(data, indent=2), encoding='utf-8')

            self._templates[template.id] = template

            return True

        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False

    def delete_template(self, template_id: str) -> bool:
        """Delete a user template."""
        template = self._templates.get(template_id)
        if not template or template.is_builtin:
            return False

        try:
            path = self._templates_dir / f"{template_id}.json"
            if path.exists():
                path.unlink()

            del self._templates[template_id]
            return True

        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return False
