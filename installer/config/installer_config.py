"""
Phase 7: Installer Configuration
Task 7.1: Installer configuration and metadata.
"""

import json
import platform
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class InstallerType(Enum):
    """Types of installers."""
    MSIX = "msix"
    INNO_SETUP = "inno_setup"
    WIX = "wix"
    PORTABLE = "portable"


class Architecture(Enum):
    """Supported architectures."""
    X64 = "x64"
    X86 = "x86"
    ARM64 = "arm64"


class WindowsVersion(Enum):
    """Minimum Windows versions."""
    WIN10_1903 = "10.0.18362.0"
    WIN10_2004 = "10.0.19041.0"
    WIN11 = "10.0.22000.0"


@dataclass
class InstallerMetadata:
    """Metadata for the installer."""
    app_name: str = "VoiceStudio"
    display_name: str = "VoiceStudio - AI Voice Synthesis"
    version: str = "1.0.0"
    publisher: str = "VoiceStudio"
    publisher_display_name: str = "VoiceStudio Team"
    description: str = "Professional AI voice synthesis and cloning studio"
    copyright: str = "Copyright © 2026 VoiceStudio"

    # Installation
    install_dir_name: str = "VoiceStudio"
    default_install_path: str = "%PROGRAMFILES%\\VoiceStudio"

    # Icons and branding
    app_icon: str = "assets/icon.ico"
    installer_icon: str = "assets/installer.ico"
    banner_image: str = "assets/banner.bmp"

    # Requirements
    min_windows_version: WindowsVersion = WindowsVersion.WIN10_2004
    architectures: list[Architecture] = field(
        default_factory=lambda: [Architecture.X64]
    )

    # Features
    requires_admin: bool = True
    create_desktop_shortcut: bool = True
    create_start_menu_entry: bool = True
    register_file_associations: bool = True

    # URLs
    website_url: str = "https://voicestudio.app"
    support_url: str = "https://voicestudio.app/support"
    update_url: str = "https://voicestudio.app/updates"


@dataclass
class FileAssociation:
    """File type association."""
    extension: str
    description: str
    icon_index: int = 0
    open_with_command: str = "\"%1\""


@dataclass
class Component:
    """Installer component."""
    id: str
    name: str
    description: str
    required: bool = False
    default_selected: bool = True
    size_mb: float = 0.0
    files: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class InstallerConfig:
    """Complete installer configuration."""
    metadata: InstallerMetadata = field(default_factory=InstallerMetadata)
    installer_type: InstallerType = InstallerType.INNO_SETUP

    # Components
    components: list[Component] = field(default_factory=list)

    # File associations
    file_associations: list[FileAssociation] = field(default_factory=list)

    # Prerequisites
    prerequisites: list[dict[str, Any]] = field(default_factory=list)

    # Post-install actions
    post_install_commands: list[str] = field(default_factory=list)

    # Uninstall
    uninstall_feedback_url: str | None = None

    def __post_init__(self):
        """Initialize default components."""
        if not self.components:
            self.components = [
                Component(
                    id="core",
                    name="Core Application",
                    description="VoiceStudio application files",
                    required=True,
                    size_mb=150.0,
                ),
                Component(
                    id="engines",
                    name="Voice Engines",
                    description="AI voice synthesis engines",
                    required=True,
                    size_mb=2000.0,
                ),
                Component(
                    id="models",
                    name="Base Models",
                    description="Pre-trained voice models",
                    default_selected=True,
                    size_mb=500.0,
                ),
                Component(
                    id="samples",
                    name="Sample Projects",
                    description="Example projects and templates",
                    default_selected=False,
                    size_mb=50.0,
                ),
                Component(
                    id="documentation",
                    name="Documentation",
                    description="User manual and guides",
                    default_selected=True,
                    size_mb=20.0,
                ),
            ]

        if not self.file_associations:
            self.file_associations = [
                FileAssociation(
                    extension=".vsproj",
                    description="VoiceStudio Project",
                ),
                FileAssociation(
                    extension=".vsarc",
                    description="VoiceStudio Archive",
                ),
                FileAssociation(
                    extension=".vsvoice",
                    description="VoiceStudio Voice Model",
                ),
            ]

        if not self.prerequisites:
            self.prerequisites = [
                {
                    "name": ".NET 8 Runtime",
                    "check": "dotnet --list-runtimes | findstr Microsoft.WindowsDesktop.App.*8",
                    "url": "https://dotnet.microsoft.com/download/dotnet/8.0",
                    "required": True,
                },
                {
                    "name": "Visual C++ Redistributable 2022",
                    "check": "reg query HKLM\\SOFTWARE\\Microsoft\\VisualStudio\\14.0\\VC\\Runtimes\\X64",
                    "url": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
                    "required": True,
                },
                {
                    "name": "Python 3.11+",
                    "check": "python --version",
                    "url": "https://www.python.org/downloads/",
                    "required": True,
                },
            ]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metadata": {
                "app_name": self.metadata.app_name,
                "display_name": self.metadata.display_name,
                "version": self.metadata.version,
                "publisher": self.metadata.publisher,
                "description": self.metadata.description,
                "copyright": self.metadata.copyright,
            },
            "installer_type": self.installer_type.value,
            "components": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "required": c.required,
                    "default_selected": c.default_selected,
                    "size_mb": c.size_mb,
                }
                for c in self.components
            ],
            "file_associations": [
                {
                    "extension": fa.extension,
                    "description": fa.description,
                }
                for fa in self.file_associations
            ],
            "prerequisites": self.prerequisites,
        }

    def save(self, path: Path) -> None:
        """Save configuration to file."""
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> "InstallerConfig":
        """Load configuration from file."""
        data = json.loads(path.read_text())

        config = cls()

        if "metadata" in data:
            for key, value in data["metadata"].items():
                if hasattr(config.metadata, key):
                    setattr(config.metadata, key, value)

        if "installer_type" in data:
            config.installer_type = InstallerType(data["installer_type"])

        return config


def get_default_config() -> InstallerConfig:
    """Get default installer configuration."""
    return InstallerConfig()


def detect_system_info() -> dict[str, Any]:
    """Detect system information for installer."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }
