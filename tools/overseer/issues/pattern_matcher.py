"""
Overseer Issue Pattern Matcher.

Matches issues against learned failure patterns for recommendation generation.
Supports simple word-overlap and TF-IDF scoring for better precision.
"""

from __future__ import annotations

import math
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.overseer.issues.config import MAX_LEARNED_PATTERNS
from tools.overseer.issues.models import Issue


@dataclass
class FailurePattern:
    """A learned or derived failure pattern for matching."""

    pattern: str
    normalized_message: str
    message_snippet: str
    context: dict[str, Any]
    timestamp: str
    issue_id: str | None = None
    resolution_confirmed: bool = False
    fix_id: str | None = None
    resolution_strategy: str = ""


def _normalize_message(message: str) -> str:
    """Normalize error message for comparison."""
    if not message:
        return ""
    s = message.lower().strip()
    s = re.sub(r"[a-z]:[\\/][^\s]+", "<path>", s)
    s = re.sub(r"/[^\s]+", "<path>", s)
    s = re.sub(r"0x[0-9a-f]+", "<hex>", s)
    s = re.sub(r"\b\d{4,}\b", "<num>", s)
    s = re.sub(r"\s+", " ", s)
    return s[:500]


def _tokenize(text: str) -> list[str]:
    """Normalize and tokenize text into words."""
    norm = _normalize_message(text)
    return [w for w in norm.split() if w]


# Python traceback: "  File \"path\", line N, in func" or "  at path (line N)"
_STACK_FILE_LINE = re.compile(
    r'(?:File\s+["\']([^"\']+)["\']|at\s+([^\s(]+))\s*(?:,\s*line\s+(\d+)|\(line\s+(\d+)\))?',
    re.I,
)


def extract_stack_frames(text: str) -> list[str]:
    """
    Extract stack trace frame identifiers from traceback/stack text.
    Returns list of normalized frame strings: "filename:line" or "filename:line:func".
    Paths are reduced to basename for grouping.
    """
    if not text or not isinstance(text, str):
        return []
    frames: list[str] = []
    for m in _STACK_FILE_LINE.finditer(text):
        path1, path2, line1, line2 = m.groups()
        path = (path1 or path2 or "").strip()
        line = line1 or line2 or "0"
        if path:
            base = os.path.basename(path.replace("\\", "/"))
            frames.append(f"{base}:{line}")
    if not frames:
        lines = text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("File ") or (line and "line " in line and " in " in line):
                frames.append(_normalize_message(line)[:200])
    return frames[:50]


def stack_frame_similarity(frames_a: list[str], frames_b: list[str]) -> float:
    """
    Similarity between two lists of stack frames (0.0-1.0).
    Uses Jaccard on frame set and optionally sequence overlap.
    """
    if not frames_a or not frames_b:
        return 0.0
    set_a = set(frames_a)
    set_b = set(frames_b)
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    if union == 0:
        return 0.0
    jaccard = inter / union
    return round(min(1.0, jaccard), 4)


def _simple_similarity(a: str, b: str) -> float:
    """
    Simple similarity score 0.0-1.0 (substring and word overlap).
    No external deps; for embeddings use optional integration later.
    """
    if not a or not b:
        return 0.0
    a_norm = _normalize_message(a)
    b_norm = _normalize_message(b)
    if a_norm == b_norm:
        return 1.0
    words_a = set(a_norm.split())
    words_b = set(b_norm.split())
    if not words_a:
        return 0.0
    overlap = len(words_a & words_b) / len(words_a)
    if a_norm in b_norm or b_norm in a_norm:
        overlap = min(1.0, overlap + 0.3)
    return round(overlap, 4)


def _tfidf_similarity(msg_a: str, msg_b: str, corpus: list[str] | None = None) -> float:
    """
    TF-IDF-weighted similarity between two messages (0.0-1.0).
    Uses corpus for IDF when provided; otherwise uses [msg_a, msg_b].
    """
    tokens_a = _tokenize(msg_a)
    tokens_b = _tokenize(msg_b)
    if not tokens_a or not tokens_b:
        return 0.0
    if corpus is None:
        corpus = [msg_a, msg_b]
    n_docs = len(corpus)
    doc_freq: Counter[str] = Counter()
    for doc in corpus:
        doc_freq.update(set(_tokenize(doc)))
    idf: dict[str, float] = {}
    for term, df in doc_freq.items():
        idf[term] = math.log((n_docs + 1) / (df + 1)) + 1.0
    tf_a: Counter[str] = Counter(tokens_a)
    tf_b: Counter[str] = Counter(tokens_b)
    vec_a = {t: tf_a[t] * idf.get(t, 1.0) for t in tf_a}
    vec_b = {t: tf_b[t] * idf.get(t, 1.0) for t in tf_b}
    dot = sum(vec_a.get(t, 0) * vec_b.get(t, 0) for t in vec_a)
    norm_a = math.sqrt(sum(x * x for x in vec_a.values()))
    norm_b = math.sqrt(sum(x * x for x in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    sim = dot / (norm_a * norm_b)
    return round(max(0.0, min(1.0, sim)), 4)


def load_learned_patterns(
    patterns_path: Path | None = None,
    root: Path | None = None,
    limit: int | None = None,
) -> list[FailurePattern]:
    """
    Load learned patterns from failure_analyzer JSONL.

    Returns list of FailurePattern, newest last, up to limit.
    """
    if limit is None:
        limit = min(MAX_LEARNED_PATTERNS, 500)
    try:
        from tools.overseer.learning.failure_analyzer import load_recent_patterns
    except ImportError:
        return []

    entries = load_recent_patterns(
        patterns_path=patterns_path,
        root=root,
        limit=limit,
    )
    result = []
    for e in entries:
        pattern = e.get("pattern", "unknown")
        snippet = e.get("message_snippet", "")[:500]
        normalized = _normalize_message(snippet)
        result.append(
            FailurePattern(
                pattern=pattern,
                normalized_message=normalized,
                message_snippet=snippet,
                context=dict(e.get("context", {})),
                timestamp=e.get("timestamp", ""),
                issue_id=e.get("issue_id"),
                resolution_confirmed=e.get("resolution_confirmed", False),
                fix_id=e.get("fix_id"),
                resolution_strategy=e.get("resolution_strategy", ""),
            )
        )
    return result


def _issue_stack_frames(issue: Issue) -> list[str]:
    """Extract stack frames from issue context (stack, traceback, error_stack)."""
    ctx = issue.context or {}
    for key in ("stack", "traceback", "error_stack"):
        if key in ctx and isinstance(ctx[key], str):
            frames = extract_stack_frames(ctx[key])
            if frames:
                return frames
    return []


def match_patterns(
    issue: Issue,
    learned: list[FailurePattern] | None = None,
    threshold: float = 0.5,
    use_tfidf: bool = True,
    use_stack_boost: bool = True,
) -> list[tuple[FailurePattern, float]]:
    """
    Find learned patterns similar to this issue.

    When use_tfidf is True and there are multiple learned patterns, TF-IDF
    scoring is used for better precision; otherwise simple word overlap is used.
    When use_stack_boost is True and both issue and pattern have stack data,
    similarity is boosted by stack frame overlap.

    Returns list of (FailurePattern, similarity) sorted by similarity descending.
    """
    if learned is None:
        learned = load_learned_patterns(limit=200)
    corpus: list[str] | None = None
    if use_tfidf and len(learned) > 0:
        corpus = [issue.message] + [fp.message_snippet for fp in learned]
    issue_frames = _issue_stack_frames(issue) if use_stack_boost else []
    matches = []
    for fp in learned:
        if use_tfidf and corpus is not None:
            sim = _tfidf_similarity(issue.message, fp.message_snippet, corpus)
        else:
            sim = _simple_similarity(issue.message, fp.message_snippet)
        if use_stack_boost and issue_frames:
            pattern_stack = (fp.context or {}).get("stack") or (fp.context or {}).get("traceback")
            if isinstance(pattern_stack, str):
                pattern_frames = extract_stack_frames(pattern_stack)
                if pattern_frames:
                    stack_sim = stack_frame_similarity(issue_frames, pattern_frames)
                    sim = round(min(1.0, sim * 0.7 + stack_sim * 0.3), 4)
        if sim >= threshold:
            matches.append((fp, sim))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches
