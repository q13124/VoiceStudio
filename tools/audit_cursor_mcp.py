"""
Audit Cursor MCP configuration (C:\\Users\\<you>\\.cursor\\mcp.json).

Goal:
- Identify MCP entries that are guaranteed to fail because their npm package does not exist (404).
- Produce a "cleaned" mcp.json that keeps:
  - non-npx servers (e.g. GitKraken stdio)
  - url-based servers (e.g. openmemory) (flag if placeholder auth)
  - npx servers whose package exists on npm (still may require API keys)

This script intentionally does NOT attempt to start every MCP server; it focuses on the most common
root cause for "almost all MCPs erroring": invalid npm package names.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

NPM_REGISTRY_BASE = "https://registry.npmjs.org/"


@dataclass(frozen=True)
class NpxPackageRef:
    package: str
    raw_args: Tuple[str, ...]


def _extract_npx_package(server_cfg: Dict[str, Any]) -> Optional[NpxPackageRef]:
    """
    Cursor MCP entries commonly look like:
      { "command": "npx", "args": ["-y", "@scope/pkg"] }
    We treat the first non-flag arg as the package name.
    """
    cmd = server_cfg.get("command")
    if cmd != "npx":
        return None

    args = server_cfg.get("args") or []
    if not isinstance(args, list):
        return None

    package = None
    for a in args:
        if not isinstance(a, str):
            continue
        if a.startswith("-"):
            continue
        package = a.strip()
        break

    if not package:
        return None

    return NpxPackageRef(package=package, raw_args=tuple(str(a) for a in args))


def _npm_registry_exists(package: str, timeout_sec: float = 7.5) -> Tuple[bool, str]:
    """
    Returns (exists, detail). 'detail' is a short string safe for reports.
    """
    # Scoped packages need encoding of slash.
    encoded = urllib.parse.quote(package, safe="@")
    url = f"{NPM_REGISTRY_BASE}{encoded}"

    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            # npm registry should return 200 for real packages.
            return (200 <= resp.status < 300), f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        # 404 is the common case for invalid packages.
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, f"error: {type(e).__name__}"


def _is_openmemory_placeholder(server_cfg: Dict[str, Any]) -> bool:
    headers = server_cfg.get("headers") or {}
    if not isinstance(headers, dict):
        return False
    auth = headers.get("Authorization")
    if not isinstance(auth, str):
        return False
    return "YOUR OPENMEMORY API KEY" in auth or "om-{" in auth


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(text)


def main(argv: list[str]) -> int:
    # Defaults
    user_profile = os.environ.get("USERPROFILE") or str(Path.home())
    default_cursor_mcp = Path(user_profile) / ".cursor" / "mcp.json"

    mcp_path = Path(argv[1]) if len(argv) > 1 else default_cursor_mcp
    out_dir = Path(argv[2]) if len(argv) > 2 else Path("docs/governance/mcp")

    if not mcp_path.exists():
        print(f"ERROR: MCP config not found: {mcp_path}", file=sys.stderr)
        return 2

    root = _load_json(mcp_path)
    servers = root.get("mcpServers") or {}
    if not isinstance(servers, dict):
        print("ERROR: mcpServers is missing or not an object", file=sys.stderr)
        return 2

    start = time.time()

    kept: Dict[str, Any] = {}
    missing: list[tuple[str, str, str]] = []  # (server_key, package, detail)
    exists: list[tuple[str, str, str]] = []  # (server_key, package, detail)
    non_npx: list[str] = []
    needs_config: list[str] = []

    # Small cache because the config can repeat packages.
    pkg_cache: Dict[str, Tuple[bool, str]] = {}

    for key, cfg in servers.items():
        if not isinstance(cfg, dict):
            continue

        if "url" in cfg:
            kept[key] = cfg
            non_npx.append(key)
            if key.lower() == "openmemory" and _is_openmemory_placeholder(cfg):
                needs_config.append(
                    "openmemory: Authorization header contains placeholder; set a real OpenMemory token"
                )
            continue

        pkg_ref = _extract_npx_package(cfg)
        if pkg_ref is None:
            kept[key] = cfg
            non_npx.append(key)
            continue

        if pkg_ref.package not in pkg_cache:
            pkg_cache[pkg_ref.package] = _npm_registry_exists(pkg_ref.package)

        ok, detail = pkg_cache[pkg_ref.package]
        if ok:
            kept[key] = cfg
            exists.append((key, pkg_ref.package, detail))
        else:
            missing.append((key, pkg_ref.package, detail))

    cleaned = {"mcpServers": kept}

    cleaned_json_path = out_dir / "cursor.mcp.cleaned.json"
    report_path = out_dir / "CURSOR_MCP_AUDIT_REPORT.md"
    _write_json(cleaned_json_path, cleaned)

    elapsed = time.time() - start

    lines: list[str] = []
    lines.append("# Cursor MCP Audit Report")
    lines.append("")
    lines.append(f"- Source: `{mcp_path}`")
    lines.append(f"- Cleaned config: `{cleaned_json_path}`")
    lines.append(f"- Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- Duration: {elapsed:.1f}s")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total servers in config: **{len(servers)}**")
    lines.append(f"- Kept in cleaned config: **{len(kept)}**")
    lines.append(
        f"- Removed because npm package missing (404/private): **{len(missing)}**"
    )
    lines.append("")
    if needs_config:
        lines.append("## Needs configuration (will still fail until fixed)")
        lines.append("")
        for item in needs_config:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("## Kept non-npx servers")
    lines.append("")
    if non_npx:
        for k in sorted(non_npx):
            lines.append(f"- `{k}`")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Kept npx servers with npm package found")
    lines.append("")
    if exists:
        for k, pkg, detail in sorted(exists, key=lambda x: (x[1], x[0])):
            lines.append(f"- `{k}` → `{pkg}` ({detail})")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Removed npx servers (npm package missing / not accessible)")
    lines.append("")
    if missing:
        for k, pkg, detail in sorted(missing, key=lambda x: (x[2], x[1], x[0])):
            lines.append(f"- `{k}` → `{pkg}` ({detail})")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Next steps (recommended)")
    lines.append("")
    lines.append("1. Replace your Cursor MCP config with the cleaned file’s contents.")
    lines.append("2. Restart Cursor.")
    lines.append(
        "3. For any MCPs you removed but actually need, re-add them only after confirming the correct package name and required API keys."
    )
    lines.append("")

    _write_text(report_path, "\n".join(lines))

    print(f"Wrote: {cleaned_json_path}")
    print(f"Wrote: {report_path}")
    print(
        f"Kept: {len(kept)} / {len(servers)} (removed {len(missing)} invalid npx packages)"
    )
    if needs_config:
        print("Needs configuration:")
        for item in needs_config:
            print(f" - {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
