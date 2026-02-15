"""
Replay Bundle

Generates debug bundles containing agent configuration, tool trace,
and context for reproducing issues.
"""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .audit_store import AuditEntry, AuditStore
from .identity import AgentIdentity
from .version_manifest import ManifestEntry, VersionManifestStore


@dataclass
class ReplayBundle:
    """
    A replay bundle for debugging agent behavior.

    Contains everything needed to reproduce an agent's actions:
    - Agent identity and configuration
    - Version manifests (prompt, tools, policy)
    - Audit trail of actions
    - Environment context
    """

    bundle_id: str
    created_at: datetime
    agent: AgentIdentity
    correlation_id: str
    manifests: dict[str, ManifestEntry]
    audit_entries: list[AuditEntry]
    environment: dict[str, str]
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "bundle_id": self.bundle_id,
            "created_at": self.created_at.isoformat(),
            "agent": self.agent.to_dict(),
            "correlation_id": self.correlation_id,
            "manifests": {k: v.to_dict() for k, v in self.manifests.items()},
            "audit_entries": [e.to_dict() for e in self.audit_entries],
            "environment": self.environment,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReplayBundle":
        """Create from dictionary."""
        return cls(
            bundle_id=data["bundle_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            agent=AgentIdentity.from_dict(data["agent"]),
            correlation_id=data["correlation_id"],
            manifests={k: ManifestEntry.from_dict(v) for k, v in data["manifests"].items()},
            audit_entries=[AuditEntry.from_dict(e) for e in data["audit_entries"]],
            environment=data.get("environment", {}),
            notes=data.get("notes", ""),
        )


class ReplayBundleGenerator:
    """
    Generates replay bundles for debugging.

    Collects agent state, configuration, and audit trail
    into a portable bundle for issue reproduction.
    """

    def __init__(
        self,
        audit_store: AuditStore | None = None,
        manifest_store: VersionManifestStore | None = None,
        output_dir: Path | None = None,
    ):
        """
        Initialize the generator.

        Args:
            audit_store: Audit store for retrieving action history
            manifest_store: Manifest store for version info
            output_dir: Directory for saving bundles
        """
        self._audit_store = audit_store or AuditStore()
        self._manifest_store = manifest_store or VersionManifestStore()

        if output_dir:
            self._output_dir = output_dir
        else:
            import os
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self._output_dir = Path(appdata) / "VoiceStudio" / "replay_bundles"

        self._output_dir.mkdir(parents=True, exist_ok=True)

    def _get_environment(self) -> dict[str, str]:
        """Capture relevant environment information."""
        import os
        import platform
        import sys

        env = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }

        # Add relevant environment variables (redact sensitive ones)
        safe_vars = [
            "PATH", "PYTHONPATH", "VIRTUAL_ENV", "CONDA_PREFIX",
            "CUDA_VISIBLE_DEVICES", "APPDATA", "USERPROFILE",
        ]
        for var in safe_vars:
            if var in os.environ:
                env[f"env_{var}"] = os.environ[var]

        return env

    def generate(
        self,
        agent: AgentIdentity,
        notes: str = "",
        include_full_trace: bool = True,
    ) -> ReplayBundle:
        """
        Generate a replay bundle for an agent.

        Args:
            agent: The agent to generate a bundle for
            notes: Optional notes about the issue
            include_full_trace: Include all actions or just failures

        Returns:
            The generated replay bundle
        """
        import uuid

        # Get audit entries for this agent/correlation
        if include_full_trace:
            entries = self._audit_store.get_by_correlation_id(agent.correlation_id)
        else:
            # Just failures
            entries = [
                e for e in self._audit_store.get_by_correlation_id(agent.correlation_id)
                if e.result in ("failure", "denied")
            ]

        # Get manifests
        manifests = {}
        for manifest in self._manifest_store.get_all():
            if manifest.content_hash == agent.config_hash:
                manifests[manifest.manifest_type.value] = manifest

        return ReplayBundle(
            bundle_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            agent=agent,
            correlation_id=agent.correlation_id,
            manifests=manifests,
            audit_entries=entries,
            environment=self._get_environment(),
            notes=notes,
        )

    def generate_for_correlation(
        self,
        correlation_id: str,
        notes: str = "",
    ) -> ReplayBundle | None:
        """
        Generate a replay bundle for a correlation ID.

        Args:
            correlation_id: The correlation ID to trace
            notes: Optional notes

        Returns:
            The generated bundle, or None if no entries found
        """
        entries = self._audit_store.get_by_correlation_id(correlation_id)
        if not entries:
            return None

        # Try to reconstruct agent identity from first entry
        first_entry = entries[0]

        import uuid

        # Create a minimal agent identity
        from .identity import AgentRole, AgentState

        agent = AgentIdentity(
            agent_id=first_entry.agent_id,
            machine_id="unknown",
            user_id=first_entry.user_id,
            role=AgentRole.CODER,  # Default
            state=AgentState.COMPLETED,
            correlation_id=correlation_id,
            session_id=first_entry.session_id,
        )

        return ReplayBundle(
            bundle_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            agent=agent,
            correlation_id=correlation_id,
            manifests={},
            audit_entries=entries,
            environment=self._get_environment(),
            notes=notes,
        )

    def save(self, bundle: ReplayBundle, format: str = "json") -> Path:
        """
        Save a bundle to disk.

        Args:
            bundle: The bundle to save
            format: Output format ("json" or "zip")

        Returns:
            Path to the saved file
        """
        timestamp = bundle.created_at.strftime("%Y%m%d_%H%M%S")
        base_name = f"replay_{bundle.bundle_id[:8]}_{timestamp}"

        if format == "zip":
            return self._save_zip(bundle, base_name)
        else:
            return self._save_json(bundle, base_name)

    def _save_json(self, bundle: ReplayBundle, base_name: str) -> Path:
        """Save as JSON file."""
        output_path = self._output_dir / f"{base_name}.json"
        output_path.write_text(
            json.dumps(bundle.to_dict(), indent=2),
            encoding="utf-8"
        )
        return output_path

    def _save_zip(self, bundle: ReplayBundle, base_name: str) -> Path:
        """Save as ZIP archive with separate files."""
        output_path = self._output_dir / f"{base_name}.zip"

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Main bundle metadata
            zf.writestr(
                "bundle.json",
                json.dumps({
                    "bundle_id": bundle.bundle_id,
                    "created_at": bundle.created_at.isoformat(),
                    "correlation_id": bundle.correlation_id,
                    "notes": bundle.notes,
                }, indent=2)
            )

            # Agent identity
            zf.writestr(
                "agent.json",
                json.dumps(bundle.agent.to_dict(), indent=2)
            )

            # Environment
            zf.writestr(
                "environment.json",
                json.dumps(bundle.environment, indent=2)
            )

            # Manifests
            for name, manifest in bundle.manifests.items():
                zf.writestr(
                    f"manifests/{name}.json",
                    json.dumps(manifest.to_dict(), indent=2)
                )

            # Audit entries
            zf.writestr(
                "audit_trace.jsonl",
                "\n".join(e.to_json_line() for e in bundle.audit_entries)
            )

        return output_path

    def load(self, path: Path) -> ReplayBundle:
        """
        Load a bundle from disk.

        Args:
            path: Path to the bundle file

        Returns:
            The loaded replay bundle
        """
        if path.suffix == ".zip":
            return self._load_zip(path)
        else:
            return self._load_json(path)

    def _load_json(self, path: Path) -> ReplayBundle:
        """Load from JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return ReplayBundle.from_dict(data)

    def _load_zip(self, path: Path) -> ReplayBundle:
        """Load from ZIP archive."""
        with zipfile.ZipFile(path, "r") as zf:
            # Read main bundle
            bundle_data = json.loads(zf.read("bundle.json"))
            agent_data = json.loads(zf.read("agent.json"))
            env_data = json.loads(zf.read("environment.json"))

            # Read manifests
            manifests = {}
            for name in zf.namelist():
                if name.startswith("manifests/") and name.endswith(".json"):
                    manifest_name = Path(name).stem
                    manifest_data = json.loads(zf.read(name))
                    manifests[manifest_name] = ManifestEntry.from_dict(manifest_data)

            # Read audit trace
            audit_entries = []
            audit_content = zf.read("audit_trace.jsonl").decode("utf-8")
            for line in audit_content.strip().split("\n"):
                if line:
                    audit_entries.append(AuditEntry.from_dict(json.loads(line)))

            return ReplayBundle(
                bundle_id=bundle_data["bundle_id"],
                created_at=datetime.fromisoformat(bundle_data["created_at"]),
                agent=AgentIdentity.from_dict(agent_data),
                correlation_id=bundle_data["correlation_id"],
                manifests=manifests,
                audit_entries=audit_entries,
                environment=env_data,
                notes=bundle_data.get("notes", ""),
            )

    def list_bundles(self) -> list[Path]:
        """List all saved bundles."""
        bundles = list(self._output_dir.glob("replay_*.json"))
        bundles.extend(self._output_dir.glob("replay_*.zip"))
        return sorted(bundles, key=lambda p: p.stat().st_mtime, reverse=True)
