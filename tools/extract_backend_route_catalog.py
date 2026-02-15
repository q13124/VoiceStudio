#!/usr/bin/env python3
"""
Extract a machine-readable catalog of FastAPI route modules.

Scans backend/api/routes/*.py and captures:
- router prefix and tags
- endpoint decorator inventory (method + path + line)

Outputs JSON for governance documentation and audits.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_utc_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


_METHODS = ("get", "post", "put", "delete", "patch", "options", "head")
_DECORATOR_RE = re.compile(
    r"""^\s*@router\.(?P<method>get|post|put|delete|patch|options|head)\(\s*(?P<quote>["'])(?P<path>[^"']+)(?P=quote)""",
    re.IGNORECASE,
)
_WS_DECORATOR_RE = re.compile(
    r"""^\s*@router\.websocket\(\s*(?P<quote>["'])(?P<path>[^"']+)(?P=quote)""",
    re.IGNORECASE,
)


def _extract_router_prefix_and_tags(text: str) -> dict[str, Any]:
    prefix: str | None = None
    tags: list[str] = []

    m_prefix = re.search(r"""APIRouter\([^)]*prefix\s*=\s*["']([^"']+)["']""", text, re.DOTALL)
    if m_prefix:
        prefix = m_prefix.group(1)

    m_tags = re.search(r"""APIRouter\([^)]*tags\s*=\s*\[([^\]]*)\]""", text, re.DOTALL)
    if m_tags:
        tags_blob = m_tags.group(1)
        tags = re.findall(r"""["']([^"']+)["']""", tags_blob)

    return {"prefix": prefix, "tags": tags}


def extract_routes_catalog(routes_root: Path) -> dict[str, Any]:
    if not routes_root.exists():
        raise FileNotFoundError(f"Routes root not found: {routes_root}")
    if not routes_root.is_dir():
        raise NotADirectoryError(f"Routes root is not a directory: {routes_root}")

    modules: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for route_file in sorted(routes_root.glob("*.py")):
        if route_file.name == "__init__.py":
            continue

        try:
            text = _read_text(route_file)
            router_meta = _extract_router_prefix_and_tags(text)

            endpoints: list[dict[str, Any]] = []
            method_counts: dict[str, int] = {m.upper(): 0 for m in _METHODS}
            ws_count = 0

            for idx, line in enumerate(text.splitlines(), start=1):
                m = _DECORATOR_RE.match(line)
                if m:
                    method = m.group("method").upper()
                    path = m.group("path")
                    method_counts[method] = method_counts.get(method, 0) + 1
                    endpoints.append({"kind": "http", "method": method, "path": path, "line": idx})
                    continue

                wsm = _WS_DECORATOR_RE.match(line)
                if wsm:
                    ws_path = wsm.group("path")
                    ws_count += 1
                    endpoints.append({"kind": "websocket", "path": ws_path, "line": idx})

            modules.append(
                {
                    "file_path": str(route_file),
                    "router_prefix": router_meta["prefix"],
                    "router_tags": router_meta["tags"],
                    "endpoint_counts": {
                        "http": {k: v for k, v in method_counts.items() if v > 0},
                        "websocket": ws_count,
                        "total": len(endpoints),
                    },
                    "endpoints": endpoints,
                }
            )
        except Exception as e:
            errors.append({"path": str(route_file), "error": type(e).__name__, "detail": str(e)})

    # Stable ordering by prefix then path
    modules.sort(
        key=lambda m: (
            (m.get("router_prefix") or "").lower(),
            (m.get("file_path", "") or "").lower(),
        )
    )

    return {
        "generated_at_utc": _now_utc_iso(),
        "routes_root": str(routes_root),
        "module_count": len(modules),
        "modules": modules,
        "errors": errors,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract backend route catalog to JSON.")
    parser.add_argument(
        "--routes-root",
        type=str,
        default="E:\\VoiceStudio\\backend\\api\\routes",
        help="Routes directory (default: E:\\\\VoiceStudio\\\\backend\\\\api\\\\routes).",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output JSON file path.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    routes_root = Path(args.routes_root).resolve()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    result = extract_routes_catalog(routes_root=routes_root)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote backend route catalog: {output}")
    print(f"Modules: {result['module_count']}")
    print(f"Errors: {len(result['errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

