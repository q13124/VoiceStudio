#!/usr/bin/env python3
"""
Replace Debug.WriteLine with ErrorLogger in C# files.
Phase 8 WS2: Debug.WriteLine Tier 2 cleanup.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path("src/VoiceStudio.App")


def classify_message(msg: str) -> str:
    """Classify message for LogDebug, LogInfo, or LogWarning."""
    lower = msg.lower()
    if any(x in lower for x in ["failed", "error", "exception", "cannot"]):
        return "LogWarning"
    if any(x in lower for x in ["navigated", "registered", "completed", "loaded", "initialized"]):
        return "LogInfo"
    return "LogDebug"


def extract_source(filepath: Path) -> str:
    """Extract source name from file path (e.g. NavigationHandler)."""
    return filepath.stem


def find_matching_paren(s: str, start: int) -> int:
    """Find the matching closing paren for the one at start."""
    depth = 1
    i = start + 1
    in_string = False
    escape = False
    while i < len(s) and depth > 0:
        c = s[i]
        if escape:
            escape = False
            i += 1
            continue
        if c == "\\" and in_string:
            escape = True
            i += 1
            continue
        if c in '"\'' and not in_string:
            in_string = c
        elif c == in_string:
            in_string = False
        elif not in_string:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
        i += 1
    return i - 1 if depth == 0 else -1


def process_file(filepath: Path) -> int:
    """Replace Debug.WriteLine in file. Returns count of replacements."""
    content = filepath.read_text(encoding="utf-8")
    if "Debug.WriteLine" not in content and "System.Diagnostics.Debug.WriteLine" not in content:
        return 0

    source = extract_source(filepath)
    count = 0
    new_content = content

    for pattern in ["Debug.WriteLine", "System.Diagnostics.Debug.WriteLine"]:
        idx = 0
        while True:
            idx = new_content.find(pattern, idx)
            if idx < 0:
                break
            paren_start = new_content.find("(", idx)
            if paren_start < 0:
                break
            paren_end = find_matching_paren(new_content, paren_start)
            if paren_end < 0:
                break
            arg = new_content[paren_start + 1:paren_end].strip()
            msg_lower = arg.lower()
            method = "LogDebug"
            if any(x in msg_lower for x in ["failed", "error", "exception"]):
                method = "LogWarning"
            elif any(x in msg_lower for x in ["navigated", "registered", "completed"]):
                method = "LogInfo"
            replacement = f'ErrorLogger.{method}({arg}, "{source}")'
            new_content = new_content[:idx] + replacement + new_content[paren_end + 1:]
            count += 1
            idx = idx + len(replacement)

    if count > 0:
        if "using VoiceStudio.App.Logging;" not in new_content:
            idx = new_content.find("using System")
            if idx >= 0:
                insert = new_content.find("\n", idx) + 1
                new_content = new_content[:insert] + "using VoiceStudio.App.Logging;\n" + new_content[insert:]
        if "Debug." not in new_content and "using System.Diagnostics;" in new_content:
            new_content = new_content.replace("using System.Diagnostics;\n", "")
        filepath.write_text(new_content, encoding="utf-8")
    return count


def main():
    total = 0
    for path in SRC.rglob("*.cs"):
        if "/obj/" in path.as_posix() or "/bin/" in path.as_posix():
            continue
        if path.name == "ErrorLogger.cs":
            continue  # ErrorLogger uses Debug.WriteLine intentionally to avoid recursion
        if "Debug.WriteLine" in path.read_text(encoding="utf-8"):
            n = process_file(path)
            if n > 0:
                print(f"  {path}: {n} replacements")
                total += n
    print(f"Total: {total} replacements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
