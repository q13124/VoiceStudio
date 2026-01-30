"""
Failure analyzer – extract and record failure patterns for meta-learning.

After errors, extract a short pattern (e.g. "XAML x:Bind failures") and store
it. Patterns can be loaded into context when a similar task is detected
(see context sources or vector memory).
"""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_PATTERNS_PATH = ".cursor/learned_failure_patterns.jsonl"
MAX_PATTERN_LEN = 200
MAX_MESSAGE_SNIPPET = 500


def extract_pattern(error_msg: str) -> str:
    """
    Extract a short, normalized pattern from an error message.

    Examples: "XAML x:Bind errors", "File not found", "ImportError: torch".
    """
    if not error_msg or not isinstance(error_msg, str):
        return "unknown"
    msg = error_msg.strip()
    if not msg:
        return "unknown"
    # First line often contains the key (exception type, file, etc.)
    first_line = msg.split("\n")[0].strip()
    # Drop paths and hex addresses for brevity
    first_line = re.sub(r"[A-Za-z]:[/\\][^\s]+", "<path>", first_line)
    first_line = re.sub(r"0x[0-9a-fA-F]+", "<addr>", first_line)
    # Take first MAX_PATTERN_LEN chars
    pattern = first_line[:MAX_PATTERN_LEN].strip()
    return pattern or "unknown"


def record_failure_pattern(
    error_msg: str,
    context: Optional[Dict[str, Any]] = None,
    patterns_path: Optional[Path] = None,
    root: Optional[Path] = None,
) -> bool:
    """
    Record a failure pattern to the learned patterns file.

    Args:
        error_msg: Raw error message
        context: Optional dict (e.g. task_id, role, phase)
        patterns_path: Override path to JSONL file
        root: Project root (used if patterns_path is relative)

    Returns:
        True if written successfully
    """
    pattern = extract_pattern(error_msg)
    snippet = (error_msg or "")[:MAX_MESSAGE_SNIPPET]
    root = root or Path(__file__).resolve().parents[3]
    path = patterns_path or root / DEFAULT_PATTERNS_PATH.replace("/", os.sep)
    path = path if path.is_absolute() else root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "pattern": pattern,
        "message_snippet": snippet,
        "context": context or {},
        "timestamp": datetime.utcnow().isoformat(),
        "tag": "learned_pattern",
    }
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        logger.debug("Failed to record failure pattern: %s", e)
        return False


def load_recent_patterns(
    patterns_path: Optional[Path] = None,
    root: Optional[Path] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Load recent learned failure patterns (for injection into context).

    Returns list of entries, newest last, up to limit.
    """
    root = root or Path(__file__).resolve().parents[3]
    path = patterns_path or root / DEFAULT_PATTERNS_PATH.replace("/", os.sep)
    path = path if path.is_absolute() else root / path
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        entries = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return entries[-limit:]
    except Exception as e:
        logger.debug("Failed to load failure patterns: %s", e)
        return []
