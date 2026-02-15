"""
Project Commands.

Task 3.2.1: Commands for project operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.application.commands.base import Command


@dataclass
class CreateProject(Command):
    """Command to create a new project."""

    name: str = ""
    description: str = ""
    output_path: str | None = None
    tags: list[str] = field(default_factory=list)
    settings: dict[str, Any] | None = None


@dataclass
class UpdateProject(Command):
    """Command to update a project."""

    project_id: str = ""
    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    settings: dict[str, Any] | None = None


@dataclass
class DeleteProject(Command):
    """Command to delete a project."""

    project_id: str = ""
    delete_files: bool = False


@dataclass
class ArchiveProject(Command):
    """Command to archive a project."""

    project_id: str = ""


@dataclass
class DuplicateProject(Command):
    """Command to duplicate a project."""

    project_id: str = ""
    new_name: str = ""
    include_audio: bool = True


@dataclass
class ExportProject(Command):
    """Command to export a project."""

    project_id: str = ""
    output_path: str = ""
    format: str = "wav"
    include_metadata: bool = True
