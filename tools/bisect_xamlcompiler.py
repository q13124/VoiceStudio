"""
Bisect WindowsAppSDK XamlCompiler.exe crashes by compiling subsets of XamlPages.

This script:
1) Reads obj/**/input.json to get the current XamlPages list (from a prior build attempt).
2) Repeatedly runs `dotnet msbuild ... /t:MarkupCompilePass1` with a custom include-file
   (one ItemSpec per line) via /p:VoiceStudioXamlDebugIncludeFile=...
3) Narrows down to the smallest set that still crashes, ideally a single XAML file.

Usage (PowerShell):
  python tools/bisect_xamlcompiler.py

Notes:
- Assumes repo layout and that `VoiceStudio_LoadXamlDebugIncludeFile` target exists in the csproj.
- Uses unique include-file names per test to avoid cross-process interference.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(r"e:\VoiceStudio")
APP_CSPROJ = REPO_ROOT / r"src\VoiceStudio.App\VoiceStudio.App.csproj"
OBJ_DIR = REPO_ROOT / r"src\VoiceStudio.App\obj"
INCLUDE_DIR = REPO_ROOT / r"xaml_bisect_tmp"


def _find_input_json() -> Path:
    # Prefer Debug input.json under net8.0-windows* first.
    candidates = list(OBJ_DIR.rglob("input.json"))
    if not candidates:
        raise FileNotFoundError(f"No input.json found under {OBJ_DIR}")

    def score(p: Path) -> Tuple[int, float]:
        s = 0
        ps = str(p).lower()
        if "\\debug\\" in ps:
            s += 10
        if "net8.0-windows" in ps:
            s += 5
        return (s, p.stat().st_mtime)

    candidates.sort(key=score, reverse=True)
    return candidates[0]


def _load_xaml_pages(input_json: Path) -> List[str]:
    data = json.loads(input_json.read_text(encoding="utf-8"))
    pages = data.get("XamlPages") or []
    # Pages are objects with ItemSpec
    items = []
    for entry in pages:
        spec = entry.get("ItemSpec")
        if spec:
            items.append(spec)
    if not items:
        raise RuntimeError(f"No XamlPages found in {input_json}")
    return items


def _write_include_file(items: List[str]) -> Path:
    INCLUDE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = f"{int(time.time() * 1000)}_{os.getpid()}"
    path = INCLUDE_DIR / f"include_{stamp}.txt"
    # Use \n explicitly; MSBuild ReadLinesFromFile expects CRLF/LF both fine.
    path.write_text("\n".join(items) + "\n", encoding="utf-8")
    return path


def _run_pass1(include_file: Path) -> int:
    cmd = [
        "dotnet",
        "msbuild",
        str(APP_CSPROJ),
        "/t:MarkupCompilePass1",
        "/v:quiet",
        f"/p:VoiceStudioXamlDebugIncludeFile={include_file}",
    ]
    # Keep output minimal; returncode is the signal.
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    # Print the first/last few lines on failure to help correlate.
    if proc.returncode != 0:
        out = proc.stdout.strip().splitlines()
        head = "\n".join(out[:30])
        tail = "\n".join(out[-30:])
        print("\n--- msbuild (failed) head ---")
        print(head)
        print("--- msbuild (failed) tail ---")
        print(tail)
        print("--- end ---\n")
    return proc.returncode


def _repro(items: List[str]) -> bool:
    include = _write_include_file(items)
    rc1 = _run_pass1(include)
    if rc1 == 0:
        return False
    # Confirm once to reduce flakiness.
    include2 = _write_include_file(items)
    rc2 = _run_pass1(include2)
    return rc2 != 0


def main() -> int:
    if not APP_CSPROJ.exists():
        print(f"Missing project: {APP_CSPROJ}", file=sys.stderr)
        return 2

    input_json = _find_input_json()
    pages = _load_xaml_pages(input_json)
    print(f"Using input.json: {input_json}")
    print(f"Total XamlPages: {len(pages)}")

    # First ensure the issue reproduces on the full set (otherwise bisect is meaningless).
    print("\nRepro check: full set ...")
    if not _repro(pages):
        print("Full set did NOT reproduce consistently; aborting bisect.")
        return 1

    lo = 0
    hi = len(pages)
    current = pages

    # Binary search: find a failing half.
    while len(current) > 1:
        mid = len(current) // 2
        left = current[:mid]
        right = current[mid:]

        print(f"\nTesting left half: {len(left)} pages")
        left_fails = _repro(left)
        if left_fails:
            current = left
            continue

        print(f"Testing right half: {len(right)} pages")
        right_fails = _repro(right)
        if right_fails:
            current = right
            continue

        # Neither half reproduces => interaction / flakiness. Fall back to linear scan.
        print(
            "\nNeither half reproduced; falling back to linear scan (may take a while)."
        )
        culprit = None
        for i, item in enumerate(current):
            print(f"  [{i+1}/{len(current)}] Testing single page: {item}")
            if _repro([item]):
                culprit = item
                break
        if culprit is None:
            print("No single page reproduced; likely multi-file interaction.")
            # Try pairs
            for i in range(len(current)):
                for j in range(i + 1, len(current)):
                    pair = [current[i], current[j]]
                    print(f"  Testing pair: {pair[0]} + {pair[1]}")
                    if _repro(pair):
                        print("Found reproducing pair.")
                        print(pair[0])
                        print(pair[1])
                        return 0
            print("No reproducing pair found in this subset.")
            return 0

        print("\nCulprit single XAML that reproduces:")
        print(culprit)
        return 0

    print("\nCulprit single XAML that reproduces:")
    print(current[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
