"""
Build Provenance for VoiceStudio Plugins.

Phase 5B M3 Enhancement: Provides build provenance metadata for plugin packages,
following SLSA (Supply-chain Levels for Software Artifacts) principles adapted
for local-first operation.

This module captures:
    - Build environment information (OS, Python version, tools)
    - Builder identification (machine ID, username - anonymizable)
    - Build timestamps and duration
    - Source code references (git commit, branch, repo)
    - Input artifact hashes
    - Build reproducibility information

The provenance data is embedded in .vspkg packages to provide transparency
about how and where the package was built.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import platform
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class BuildType(Enum):
    """Type of build that created the artifact."""
    
    DEVELOPMENT = "development"     # Local development build
    CI = "ci"                       # Continuous integration build
    RELEASE = "release"             # Official release build
    UNKNOWN = "unknown"


class ProvenanceVersion(Enum):
    """Provenance specification version."""
    
    V1 = "1.0"  # Initial version


@dataclass
class SourceInfo:
    """Information about the source code used for the build."""
    
    repository: Optional[str] = None          # Git repository URL (optional, local-first)
    commit: Optional[str] = None              # Git commit hash
    branch: Optional[str] = None              # Git branch name
    tag: Optional[str] = None                 # Git tag if applicable
    dirty: bool = False                       # Whether working tree had uncommitted changes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "repository": self.repository,
            "commit": self.commit,
            "branch": self.branch,
            "tag": self.tag,
            "dirty": self.dirty,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SourceInfo:
        """Create from dictionary."""
        return cls(
            repository=data.get("repository"),
            commit=data.get("commit"),
            branch=data.get("branch"),
            tag=data.get("tag"),
            dirty=data.get("dirty", False),
        )


@dataclass
class BuilderInfo:
    """Information about the build environment and builder."""
    
    # Machine information
    hostname: str = ""                        # Machine hostname (can be anonymized)
    machine_id: Optional[str] = None          # Unique machine identifier (optional)
    
    # Operating system
    os_name: str = ""                         # Operating system name
    os_version: str = ""                      # Operating system version
    os_release: str = ""                      # Operating system release
    
    # Python environment
    python_version: str = ""                  # Python version
    python_implementation: str = ""           # Python implementation (CPython, PyPy)
    
    # User information (optional, privacy-respecting)
    username: Optional[str] = None            # Username (can be anonymized)
    
    # Additional context
    ci_platform: Optional[str] = None         # CI platform if running in CI
    ci_run_id: Optional[str] = None           # CI run identifier
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hostname": self.hostname,
            "machine_id": self.machine_id,
            "os": {
                "name": self.os_name,
                "version": self.os_version,
                "release": self.os_release,
            },
            "python": {
                "version": self.python_version,
                "implementation": self.python_implementation,
            },
            "username": self.username,
            "ci_platform": self.ci_platform,
            "ci_run_id": self.ci_run_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BuilderInfo:
        """Create from dictionary."""
        os_info = data.get("os", {})
        python_info = data.get("python", {})
        
        return cls(
            hostname=data.get("hostname", ""),
            machine_id=data.get("machine_id"),
            os_name=os_info.get("name", ""),
            os_version=os_info.get("version", ""),
            os_release=os_info.get("release", ""),
            python_version=python_info.get("version", ""),
            python_implementation=python_info.get("implementation", ""),
            username=data.get("username"),
            ci_platform=data.get("ci_platform"),
            ci_run_id=data.get("ci_run_id"),
        )


@dataclass
class InputArtifact:
    """Represents an input artifact used during the build."""
    
    name: str                                 # Artifact name
    path: str                                 # Path within the plugin
    digest: Dict[str, str] = field(default_factory=dict)  # Hash digests
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "digest": self.digest,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> InputArtifact:
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            digest=data.get("digest", {}),
        )


@dataclass
class Provenance:
    """
    Build provenance metadata for a plugin package.
    
    Captures comprehensive build information following SLSA principles,
    adapted for local-first operation where remote attestation services
    are not required.
    """
    
    # Provenance metadata
    provenance_id: str = ""                   # Unique identifier for this provenance
    spec_version: str = ProvenanceVersion.V1.value
    
    # Subject (what was built)
    subject_name: str = ""                    # Package name
    subject_version: str = ""                 # Package version
    subject_digest: Dict[str, str] = field(default_factory=dict)  # Package hashes
    
    # Build information
    build_type: BuildType = BuildType.DEVELOPMENT
    build_started_at: str = ""                # ISO 8601 timestamp
    build_finished_at: str = ""               # ISO 8601 timestamp
    build_duration_ms: int = 0                # Build duration in milliseconds
    
    # Builder and source
    builder: BuilderInfo = field(default_factory=BuilderInfo)
    source: SourceInfo = field(default_factory=SourceInfo)
    
    # Input artifacts
    input_artifacts: List[InputArtifact] = field(default_factory=list)
    
    # Build configuration
    build_config: Dict[str, Any] = field(default_factory=dict)
    
    # Reproducibility
    reproducible: bool = False                # Whether build is reproducible
    reproducibility_notes: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize provenance ID if not set."""
        if not self.provenance_id:
            self.provenance_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "_type": "https://in-toto.io/Statement/v0.1",
            "provenance_id": self.provenance_id,
            "spec_version": self.spec_version,
            "subject": {
                "name": self.subject_name,
                "version": self.subject_version,
                "digest": self.subject_digest,
            },
            "build": {
                "type": self.build_type.value,
                "started_at": self.build_started_at,
                "finished_at": self.build_finished_at,
                "duration_ms": self.build_duration_ms,
            },
            "builder": self.builder.to_dict(),
            "source": self.source.to_dict(),
            "input_artifacts": [a.to_dict() for a in self.input_artifacts],
            "build_config": self.build_config,
            "reproducibility": {
                "reproducible": self.reproducible,
                "notes": self.reproducibility_notes,
            },
            "metadata": self.metadata,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def save(self, path: Path) -> None:
        """Save provenance to JSON file."""
        path.write_text(self.to_json(), encoding="utf-8")
        logger.info(f"Saved provenance to {path}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Provenance:
        """Create from dictionary."""
        subject = data.get("subject", {})
        build = data.get("build", {})
        reproducibility = data.get("reproducibility", {})
        
        return cls(
            provenance_id=data.get("provenance_id", ""),
            spec_version=data.get("spec_version", ProvenanceVersion.V1.value),
            subject_name=subject.get("name", ""),
            subject_version=subject.get("version", ""),
            subject_digest=subject.get("digest", {}),
            build_type=BuildType(build.get("type", "unknown")),
            build_started_at=build.get("started_at", ""),
            build_finished_at=build.get("finished_at", ""),
            build_duration_ms=build.get("duration_ms", 0),
            builder=BuilderInfo.from_dict(data.get("builder", {})),
            source=SourceInfo.from_dict(data.get("source", {})),
            input_artifacts=[
                InputArtifact.from_dict(a)
                for a in data.get("input_artifacts", [])
            ],
            build_config=data.get("build_config", {}),
            reproducible=reproducibility.get("reproducible", False),
            reproducibility_notes=reproducibility.get("notes"),
            metadata=data.get("metadata", {}),
        )
    
    @classmethod
    def load(cls, path: Path) -> Provenance:
        """Load provenance from JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)


class ProvenanceGenerator:
    """
    Generates build provenance for plugin packages.
    
    Collects build environment information, source code details,
    and creates a comprehensive provenance record.
    """
    
    def __init__(
        self,
        plugin_path: Path,
        package_name: Optional[str] = None,
        package_version: Optional[str] = None,
        anonymize: bool = False,
    ):
        """
        Initialize provenance generator.
        
        Args:
            plugin_path: Path to the plugin directory
            package_name: Package name (defaults to directory name)
            package_version: Package version
            anonymize: Whether to anonymize user/machine info
        """
        self.plugin_path = Path(plugin_path)
        self.package_name = package_name or self.plugin_path.name
        self.package_version = package_version or "0.0.0"
        self.anonymize = anonymize
        
        self._build_started: Optional[datetime] = None
        self._build_finished: Optional[datetime] = None
    
    def start_build(self) -> None:
        """Mark the build as started."""
        self._build_started = datetime.now(timezone.utc)
    
    def finish_build(self) -> None:
        """Mark the build as finished."""
        self._build_finished = datetime.now(timezone.utc)
    
    def generate(
        self,
        package_path: Optional[Path] = None,
        build_type: BuildType = BuildType.DEVELOPMENT,
        build_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Provenance:
        """
        Generate provenance for a plugin package.
        
        Args:
            package_path: Path to the built package (for hash computation)
            build_type: Type of build
            build_config: Build configuration used
            metadata: Additional metadata
            
        Returns:
            Provenance object with complete build information
        """
        # Ensure build times are set
        if not self._build_started:
            self._build_started = datetime.now(timezone.utc)
        if not self._build_finished:
            self._build_finished = datetime.now(timezone.utc)
        
        duration_ms = int(
            (self._build_finished - self._build_started).total_seconds() * 1000
        )
        
        provenance = Provenance(
            subject_name=self.package_name,
            subject_version=self.package_version,
            build_type=build_type,
            build_started_at=self._build_started.isoformat(),
            build_finished_at=self._build_finished.isoformat(),
            build_duration_ms=duration_ms,
            builder=self._collect_builder_info(),
            source=self._collect_source_info(),
            input_artifacts=self._collect_input_artifacts(),
            build_config=build_config or {},
            metadata=metadata or {},
        )
        
        # Compute package digest if path provided
        if package_path and package_path.exists():
            provenance.subject_digest = self._compute_file_digests(package_path)
        
        return provenance
    
    def _collect_builder_info(self) -> BuilderInfo:
        """Collect information about the build environment."""
        info = BuilderInfo(
            hostname=self._maybe_anonymize(platform.node()),
            os_name=platform.system(),
            os_version=platform.version(),
            os_release=platform.release(),
            python_version=platform.python_version(),
            python_implementation=platform.python_implementation(),
        )
        
        # Username (anonymize if requested)
        try:
            username = os.getlogin()
            info.username = self._maybe_anonymize(username)
        except OSError:
            info.username = None
        
        # Generate machine ID from hostname + OS info
        machine_str = f"{platform.node()}-{platform.system()}-{platform.machine()}"
        info.machine_id = hashlib.sha256(machine_str.encode()).hexdigest()[:16]
        
        # Detect CI environment
        info.ci_platform, info.ci_run_id = self._detect_ci_environment()
        
        return info
    
    def _collect_source_info(self) -> SourceInfo:
        """Collect information about the source code."""
        info = SourceInfo()
        
        # Try to get git information
        git_info = self._get_git_info()
        if git_info:
            info.repository = git_info.get("repository")
            info.commit = git_info.get("commit")
            info.branch = git_info.get("branch")
            info.tag = git_info.get("tag")
            info.dirty = git_info.get("dirty", False)
        
        return info
    
    def _collect_input_artifacts(self) -> List[InputArtifact]:
        """Collect information about input artifacts."""
        artifacts = []
        
        if not self.plugin_path.exists():
            return artifacts
        
        # Include key files as input artifacts
        key_files = [
            "plugin.json",
            "manifest.json",
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
        ]
        
        for filename in key_files:
            filepath = self.plugin_path / filename
            if filepath.exists():
                artifacts.append(InputArtifact(
                    name=filename,
                    path=filename,
                    digest=self._compute_file_digests(filepath),
                ))
        
        # Also include main Python files
        for py_file in self.plugin_path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            artifacts.append(InputArtifact(
                name=py_file.name,
                path=py_file.name,
                digest=self._compute_file_digests(py_file),
            ))
        
        return artifacts
    
    def _get_git_info(self) -> Optional[Dict[str, Any]]:
        """Get git repository information."""
        if not self.plugin_path.exists():
            return None
        
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.plugin_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return None
            
            info: Dict[str, Any] = {}
            
            # Get commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.plugin_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                info["commit"] = result.stdout.strip()
            
            # Get branch name
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.plugin_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                info["branch"] = result.stdout.strip()
            
            # Get remote URL (optional for local-first)
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.plugin_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                info["repository"] = result.stdout.strip()
            
            # Check if working tree is dirty
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.plugin_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                info["dirty"] = bool(result.stdout.strip())
            
            # Get tag if HEAD is tagged
            result = subprocess.run(
                ["git", "describe", "--tags", "--exact-match", "HEAD"],
                cwd=self.plugin_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                info["tag"] = result.stdout.strip()
            
            return info
            
        except (subprocess.SubprocessError, FileNotFoundError):
            return None
    
    def _detect_ci_environment(self) -> tuple[Optional[str], Optional[str]]:
        """Detect if running in a CI environment."""
        # GitHub Actions
        if os.environ.get("GITHUB_ACTIONS"):
            return "github-actions", os.environ.get("GITHUB_RUN_ID")
        
        # GitLab CI
        if os.environ.get("GITLAB_CI"):
            return "gitlab-ci", os.environ.get("CI_JOB_ID")
        
        # Azure Pipelines
        if os.environ.get("TF_BUILD"):
            return "azure-pipelines", os.environ.get("BUILD_BUILDID")
        
        # Jenkins
        if os.environ.get("JENKINS_URL"):
            return "jenkins", os.environ.get("BUILD_NUMBER")
        
        # CircleCI
        if os.environ.get("CIRCLECI"):
            return "circleci", os.environ.get("CIRCLE_BUILD_NUM")
        
        # Travis CI
        if os.environ.get("TRAVIS"):
            return "travis-ci", os.environ.get("TRAVIS_BUILD_ID")
        
        # Generic CI indicator
        if os.environ.get("CI"):
            return "generic-ci", None
        
        return None, None
    
    def _compute_file_digests(self, path: Path) -> Dict[str, str]:
        """Compute cryptographic digests for a file."""
        digests = {}
        
        try:
            content = path.read_bytes()
            digests["sha256"] = hashlib.sha256(content).hexdigest()
            digests["sha512"] = hashlib.sha512(content).hexdigest()
        except OSError as e:
            logger.warning(f"Failed to compute digests for {path}: {e}")
        
        return digests
    
    def _maybe_anonymize(self, value: str) -> str:
        """Anonymize a value if anonymization is enabled."""
        if self.anonymize:
            return hashlib.sha256(value.encode()).hexdigest()[:12]
        return value


# =============================================================================
# Convenience Functions
# =============================================================================


def generate_provenance(
    plugin_path: Path,
    package_path: Optional[Path] = None,
    package_name: Optional[str] = None,
    package_version: Optional[str] = None,
    build_type: BuildType = BuildType.DEVELOPMENT,
    build_config: Optional[Dict[str, Any]] = None,
    anonymize: bool = False,
) -> Provenance:
    """
    Generate provenance for a plugin package.
    
    Convenience function that creates a ProvenanceGenerator and generates
    provenance in a single call.
    
    Args:
        plugin_path: Path to the plugin directory
        package_path: Path to the built package (for digest computation)
        package_name: Package name
        package_version: Package version
        build_type: Type of build
        build_config: Build configuration
        anonymize: Whether to anonymize user/machine info
        
    Returns:
        Generated provenance object
    """
    generator = ProvenanceGenerator(
        plugin_path=plugin_path,
        package_name=package_name,
        package_version=package_version,
        anonymize=anonymize,
    )
    
    return generator.generate(
        package_path=package_path,
        build_type=build_type,
        build_config=build_config,
    )


def load_provenance(path: Path) -> Provenance:
    """
    Load provenance from a JSON file.
    
    Args:
        path: Path to the provenance JSON file
        
    Returns:
        Loaded provenance object
    """
    return Provenance.load(path)


def verify_provenance_digest(
    provenance: Provenance,
    package_path: Path,
) -> bool:
    """
    Verify that a package matches its provenance digest.
    
    Args:
        provenance: Provenance object with expected digest
        package_path: Path to the package to verify
        
    Returns:
        True if digest matches, False otherwise
    """
    if not package_path.exists():
        logger.error(f"Package not found: {package_path}")
        return False
    
    if not provenance.subject_digest:
        logger.warning("Provenance has no digest to verify")
        return False
    
    # Compute actual digest
    try:
        content = package_path.read_bytes()
        actual_sha256 = hashlib.sha256(content).hexdigest()
    except OSError as e:
        logger.error(f"Failed to read package: {e}")
        return False
    
    expected_sha256 = provenance.subject_digest.get("sha256")
    if not expected_sha256:
        logger.warning("Provenance has no SHA256 digest")
        return False
    
    if actual_sha256 != expected_sha256:
        logger.error(
            f"Digest mismatch: expected {expected_sha256}, got {actual_sha256}"
        )
        return False
    
    logger.info("Provenance digest verified successfully")
    return True
