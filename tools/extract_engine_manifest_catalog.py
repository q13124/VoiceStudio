#!/usr/bin/env python3
"""
Extract a machine-readable catalog of engine manifests.

Scans a given engines root directory (default: E:\\VoiceStudio\\engines) for:
- engine.manifest.json
- runtime.manifest.json

Outputs a JSON catalog suitable for governance documentation and audits.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _now_utc_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _split_entry_point(entry_point: str) -> Tuple[str, str]:
    """
    Returns (module_path, symbol_name) for an entry point like:
    app.core.engines.xtts_engine.XTTSEngine
    """
    parts = entry_point.split(".")
    if len(parts) < 2:
        return entry_point, ""
    return ".".join(parts[:-1]), parts[-1]


def _python_module_to_repo_path(module_path: str) -> str:
    return module_path.replace(".", "/") + ".py"


@dataclass(frozen=True)
class EngineManifestRecord:
    kind: str  # engine_manifest | runtime_manifest
    engine_id: str
    display_name: str
    engine_type: Optional[str]
    engine_subtype: Optional[str]
    version: Optional[str]
    manifest_path: str
    entry_point: Optional[str]
    entry_module: Optional[str]
    entry_symbol: Optional[str]
    entry_repo_path: Optional[str]
    entry_repo_path_exists: Optional[bool]
    tasks: List[str]
    capabilities: List[str]
    dependencies: Dict[str, Any]

    def to_json_obj(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "engine_id": self.engine_id,
            "display_name": self.display_name,
            "type": self.engine_type,
            "subtype": self.engine_subtype,
            "version": self.version,
            "manifest_path": self.manifest_path,
            "entry_point": self.entry_point,
            "entry_module": self.entry_module,
            "entry_symbol": self.entry_symbol,
            "entry_repo_path": self.entry_repo_path,
            "entry_repo_path_exists": self.entry_repo_path_exists,
            "tasks": self.tasks,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
        }


def extract_catalog(repo_root: Path, engines_root: Path) -> Dict[str, Any]:
    if not engines_root.exists():
        raise FileNotFoundError(f"Engines root not found: {engines_root}")
    if not engines_root.is_dir():
        raise NotADirectoryError(f"Engines root is not a directory: {engines_root}")

    records: List[EngineManifestRecord] = []
    errors: List[Dict[str, str]] = []

    for manifest_path in sorted(engines_root.rglob("engine.manifest.json")):
        try:
            data = _read_json(manifest_path)
            engine_id = str(data.get("engine_id") or "")
            if not engine_id:
                raise ValueError("Missing engine_id")

            display_name = str(data.get("name") or engine_id)
            engine_type = data.get("type")
            engine_subtype = data.get("subtype")
            version = data.get("version")
            entry_point = data.get("entry_point")

            entry_module = None
            entry_symbol = None
            entry_repo_path = None
            entry_repo_path_exists = None
            if isinstance(entry_point, str) and entry_point:
                entry_module, entry_symbol = _split_entry_point(entry_point)
                entry_repo_path = _python_module_to_repo_path(entry_module)
                entry_repo_path_exists = (repo_root / entry_repo_path).exists()

            deps: Dict[str, Any]
            raw_deps = data.get("dependencies", {})
            if isinstance(raw_deps, dict):
                deps = raw_deps
            elif isinstance(raw_deps, list):
                deps = {"__list__": raw_deps}
            else:
                deps = {"__raw__": raw_deps}

            tasks: List[str] = []
            if isinstance(data.get("tasks"), list):
                tasks = [str(t) for t in data["tasks"]]

            capabilities: List[str] = []
            if isinstance(data.get("capabilities"), list):
                capabilities = [str(c) for c in data["capabilities"]]

            records.append(
                EngineManifestRecord(
                    kind="engine_manifest",
                    engine_id=engine_id,
                    display_name=display_name,
                    engine_type=str(engine_type) if engine_type is not None else None,
                    engine_subtype=str(engine_subtype) if engine_subtype is not None else None,
                    version=str(version) if version is not None else None,
                    manifest_path=str(manifest_path),
                    entry_point=str(entry_point) if entry_point is not None else None,
                    entry_module=entry_module,
                    entry_symbol=entry_symbol,
                    entry_repo_path=entry_repo_path,
                    entry_repo_path_exists=entry_repo_path_exists,
                    tasks=tasks,
                    capabilities=capabilities,
                    dependencies=deps,
                )
            )
        except Exception as e:
            errors.append({"path": str(manifest_path), "error": type(e).__name__, "detail": str(e)})

    for manifest_path in sorted(engines_root.rglob("runtime.manifest.json")):
        try:
            data = _read_json(manifest_path)
            engine_id = str(data.get("id") or "")
            if not engine_id:
                raise ValueError("Missing id")

            display_name = str(data.get("displayName") or engine_id)
            engine_type = data.get("type")
            version = data.get("version")

            tasks: List[str] = []
            if isinstance(data.get("tasks"), list):
                tasks = [str(t) for t in data["tasks"]]

            entry_point = None
            entry_module = None
            entry_symbol = None
            entry_repo_path = None
            entry_repo_path_exists = None

            deps: Dict[str, Any] = {}
            records.append(
                EngineManifestRecord(
                    kind="runtime_manifest",
                    engine_id=engine_id,
                    display_name=display_name,
                    engine_type=str(engine_type) if engine_type is not None else None,
                    engine_subtype=None,
                    version=str(version) if version is not None else None,
                    manifest_path=str(manifest_path),
                    entry_point=entry_point,
                    entry_module=entry_module,
                    entry_symbol=entry_symbol,
                    entry_repo_path=entry_repo_path,
                    entry_repo_path_exists=entry_repo_path_exists,
                    tasks=tasks,
                    capabilities=[],
                    dependencies=deps,
                )
            )
        except Exception as e:
            errors.append({"path": str(manifest_path), "error": type(e).__name__, "detail": str(e)})

    records.sort(key=lambda r: (r.kind, (r.engine_type or ""), r.engine_id))

    counts: Dict[str, int] = {}
    for r in records:
        counts[r.kind] = counts.get(r.kind, 0) + 1

    return {
        "generated_at_utc": _now_utc_iso(),
        "repo_root": str(repo_root),
        "engines_root": str(engines_root),
        "counts": counts,
        "records": [r.to_json_obj() for r in records],
        "errors": errors,
    }


def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract engine manifest catalog to JSON.")
    parser.add_argument(
        "--repo-root",
        type=str,
        default="E:\\VoiceStudio",
        help="Repository root path (default: E:\\\\VoiceStudio).",
    )
    parser.add_argument(
        "--engines-root",
        type=str,
        default="E:\\VoiceStudio\\engines",
        help="Engines root path (default: E:\\\\VoiceStudio\\\\engines).",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output JSON file path.",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = _parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    engines_root = Path(args.engines_root).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    result = extract_catalog(repo_root=repo_root, engines_root=engines_root)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote engine manifest catalog: {output}")
    print(f"Counts: {result['counts']}")
    print(f"Errors: {len(result['errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

