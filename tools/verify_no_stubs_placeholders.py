#!/usr/bin/env python3
"""
RuleGuard: No stubs, placeholders, bookmarks, or tags.

Scans code for forbidden patterns. Fails the build when violations are found.
Used in Clean Build Workflow (step 5) and CI. See QUALITY_LEDGER and
docs/governance/roles/ROLE_2_BUILD_TOOLING_GUIDE.md.

Usage:
    python tools/verify_no_stubs_placeholders.py
    python tools/verify_no_stubs_placeholders.py --allowlist .ruleguard-allowlist
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union

# Project root (tools/verify_no_stubs_placeholders.py -> parent of tools)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# High-confidence violation patterns (stubs/placeholders)
FORBIDDEN = [
    (r"\bNotImplementedError\b", "not_implemented_py", "Python NotImplementedError"),
    (r"\bNotImplementedException\b", "not_implemented_cs", "C# NotImplementedException"),
    (r"raise\s+NotImplementedError", "raise_not_implemented", "raise NotImplementedError"),
    (r"throw\s+new\s+NotImplementedException", "throw_not_implemented", "throw NotImplementedException"),
    (r"\[PLACEHOLDER\]", "placeholder_bracket", "[PLACEHOLDER] literal"),
    (r"\bPLACEHOLDER\b", "placeholder_word", "PLACEHOLDER keyword"),
    (r"#\s*TODO\b", "todo_py", "TODO comment (#)"),
    (r"//\s*TODO\b", "todo_cs", "TODO comment (//)"),
    (r"#\s*FIXME\b", "fixme_py", "FIXME comment (#)"),
    (r"//\s*FIXME\b", "fixme_cs", "FIXME comment (//)"),
    (r"#\s*HACK\b", "hack_py", "HACK comment (#)"),
    (r"//\s*HACK\b", "hack_cs", "HACK comment (//)"),
]

# Code file extensions only (no markdown/docs to reduce noise)
CODE_EXTENSIONS = {".py", ".cs", ".xaml", ".js", ".ts", ".tsx", ".jsx"}

# Directories to skip
EXCLUDE_DIRS = {
    "__pycache__", ".git", "node_modules", "bin", "obj", ".vs", ".vscode",
    "venv", "env", ".venv", "build", "dist", ".buildlogs", "packages",
}

# Paths relative to PROJECT_ROOT to scan
SCAN_DIRS = ["src", "backend", "app", "tools"]

# Files that define or implement stub/placeholder checks — do not scan
EXCLUDE_FILES = {
    "tools/verify_no_stubs_placeholders.py",
    "tools/verify_non_mock.py",
}


def _compile_patterns() -> List[Tuple[re.Pattern[str], str, str]]:
    return [(re.compile(pat, re.IGNORECASE), tid, desc) for pat, tid, desc in FORBIDDEN]


def _load_allowlist(path: Path) -> Set[Tuple[str, int]]:
    """Load (path, line) allowlist; line 0 means whole file. Paths repo-relative, normalized."""
    out: Set[Tuple[str, int]] = set()
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.split("#")[0].strip()
        if not line:
            continue
        part = line.split(":", 1)
        rel = part[0].strip().replace("\\", "/")
        try:
            ln = int(part[1].strip()) if len(part) > 1 else 0
        except (ValueError, IndexError):
            ln = 0
        out.add((rel, ln))
    return out


def _is_allowed(rel_path: str, line_num: int, allowlist: Set[Tuple[str, int]]) -> bool:
    norm = rel_path.replace("\\", "/")
    if (norm, 0) in allowlist or (norm, line_num) in allowlist:
        return True
    return False


def scan_file(
    path: Path,
    rel_path: str,
    patterns: List[Tuple[re.Pattern[str], str, str]],
    allowlist: Set[Tuple[str, int]],
) -> List[Dict[str, Union[str, int]]]:
    violations: List[Dict[str, str | int]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return violations
    for line_num, line in enumerate(text.splitlines(), 1):
        for regex, tid, desc in patterns:
            if regex.search(line) and not _is_allowed(rel_path, line_num, allowlist):
                violations.append({
                    "file": rel_path,
                    "line": line_num,
                    "id": tid,
                    "desc": desc,
                    "content": line.strip()[:100],
                })
    return violations


def main() -> int:
    ap = argparse.ArgumentParser(
        description="RuleGuard: verify no stubs, placeholders, bookmarks, or tags"
    )
    ap.add_argument(
        "--allowlist",
        type=Path,
        default=PROJECT_ROOT / ".ruleguard-allowlist",
        help="Path to allowlist file (default: .ruleguard-allowlist in repo root)",
    )
    ap.add_argument(
        "--path",
        type=Path,
        default=None,
        help="Override: scan only this path (file or dir)",
    )
    args = ap.parse_args()
    allowlist_path = args.allowlist.resolve() if args.allowlist else PROJECT_ROOT / ".ruleguard-allowlist"
    allowlist = _load_allowlist(allowlist_path)

    patterns = _compile_patterns()
    all_violations: List[Dict[str, Union[str, int]]] = []
    root_str = str(PROJECT_ROOT)

    if args.path is not None:
        start = (PROJECT_ROOT / args.path).resolve() if not Path(args.path).is_absolute() else Path(args.path).resolve()
        if not start.exists():
            print(f"RuleGuard: path does not exist: {start}", file=sys.stderr)
            return 1
        dirs_to_scan = [start]
    else:
        dirs_to_scan = [PROJECT_ROOT / d for d in SCAN_DIRS if (PROJECT_ROOT / d).exists()]

    for base in dirs_to_scan:
        if not base.exists():
            continue
        if base.is_file():
            files = [base]
        else:
            files = [f for f in base.rglob("*") if f.is_file()]
        for f in files:
            if any(ex in f.parts for ex in EXCLUDE_DIRS):
                continue
            if f.suffix.lower() not in CODE_EXTENSIONS:
                continue
            try:
                rel = f.relative_to(PROJECT_ROOT)
            except ValueError:
                rel = f
            rel_path = str(rel).replace("\\", "/")
            if rel_path in EXCLUDE_FILES:
                continue
            vs = scan_file(f, rel_path, patterns, allowlist)
            all_violations.extend(vs)

    if not all_violations:
        print("RuleGuard: no stubs, placeholders, or forbidden comments detected.")
        return 0

    print("RuleGuard: violations (no stubs/placeholders/TODO/FIXME/HACK/NotImplemented):", file=sys.stderr)
    for v in sorted(all_violations, key=lambda x: (x["file"], x["line"])):
        print(f"  {v['file']}:{v['line']} [{v['id']}] {v['desc']}", file=sys.stderr)
        print(f"    {v['content']}", file=sys.stderr)
    print(f"\nTotal: {len(all_violations)} violation(s). Add paths/lines to .ruleguard-allowlist to allow.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
