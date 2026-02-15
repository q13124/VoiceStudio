#!/usr/bin/env python3
"""
Drive inventory generator for VoiceStudio governance.

This script scans a root path (default: E:\\) and produces a JSON inventory with:
- aggregated file counts by extension
- aggregated total bytes
- aggregated directory and file counts
- latest modification timestamps
- scan errors (access denied, broken links, etc.)

It is intended for evidence-based oversight and recovery work.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def _utc_iso_from_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _now_utc_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _safe_rel_parts(root: Path, path: Path) -> tuple[str, ...]:
    try:
        rel = path.relative_to(root)
    except ValueError:
        # Different drive letter or non-ancestor; treat as opaque.
        return ()
    parts = tuple(p for p in rel.parts if p not in (".",))
    return parts


def _bucket_key_for_dir(root: Path, rel_dir_parts: tuple[str, ...], depth: int) -> str:
    if depth == 0:
        return str(root)
    return str(root.joinpath(*rel_dir_parts[:depth]))


@dataclass
class AggStats:
    file_count: int = 0
    dir_count: int = 0
    total_bytes: int = 0
    ext_counts: dict[str, int] = None
    latest_mtime_ts: float | None = None

    def __post_init__(self) -> None:
        if self.ext_counts is None:
            self.ext_counts = {}

    def update_latest_mtime(self, mtime_ts: float) -> None:
        if self.latest_mtime_ts is None or mtime_ts > self.latest_mtime_ts:
            self.latest_mtime_ts = mtime_ts

    def add_file(self, file_path: Path, size_bytes: int, mtime_ts: float) -> None:
        self.file_count += 1
        self.total_bytes += int(size_bytes)

        ext = file_path.suffix.lower()
        if not ext:
            ext = "<none>"
        self.ext_counts[ext] = self.ext_counts.get(ext, 0) + 1
        self.update_latest_mtime(mtime_ts)

    def add_dir(self, mtime_ts: float) -> None:
        self.dir_count += 1
        self.update_latest_mtime(mtime_ts)

    def merge(self, other: AggStats) -> None:
        self.file_count += other.file_count
        self.dir_count += other.dir_count
        self.total_bytes += other.total_bytes
        for ext, count in other.ext_counts.items():
            self.ext_counts[ext] = self.ext_counts.get(ext, 0) + count
        if other.latest_mtime_ts is not None:
            self.update_latest_mtime(other.latest_mtime_ts)

    def to_json_obj(self) -> dict[str, object]:
        latest_mtime_utc = None
        if self.latest_mtime_ts is not None:
            latest_mtime_utc = _utc_iso_from_ts(self.latest_mtime_ts)
        return {
            "file_count": self.file_count,
            "dir_count": self.dir_count,
            "total_bytes": self.total_bytes,
            "ext_counts": dict(sorted(self.ext_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
            "latest_mtime_utc": latest_mtime_utc,
        }


def _classify_top_level_name(name: str) -> str:
    n = name.strip().lower()
    if n == "voicestudio":
        return "product_source"
    if n == "error audits":
        return "audit_bundle"
    if n in {"$recycle.bin", "system volume information"}:
        return "system"
    if n in {"cursor", ".cursor"}:
        return "tooling_cache"
    return "unclassified"


def scan_drive(root: Path, max_depth: int, follow_symlinks: bool) -> dict[str, object]:
    root = root.resolve()
    if not root.exists():
        raise FileNotFoundError(f"Root path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Root path is not a directory: {root}")

    stats_by_bucket: dict[str, AggStats] = {}
    errors: list[dict[str, str]] = []

    def get_bucket(key: str) -> AggStats:
        bucket = stats_by_bucket.get(key)
        if bucket is None:
            bucket = AggStats()
            stats_by_bucket[key] = bucket
        return bucket

    root_key = str(root)
    root_files_key = f"{root_key}::ROOT_FILES"

    def update_dir_buckets(dir_path: Path, mtime_ts: float) -> None:
        rel_parts = _safe_rel_parts(root, dir_path)
        max_bucket_depth = min(max_depth, len(rel_parts))
        for depth in range(0, max_bucket_depth + 1):
            key = _bucket_key_for_dir(root, rel_parts, depth)
            get_bucket(key).add_dir(mtime_ts)

    def update_file_buckets(file_path: Path, size_bytes: int, mtime_ts: float) -> None:
        rel_dir_parts = _safe_rel_parts(root, file_path.parent)
        if rel_dir_parts == ():
            # File directly under root
            get_bucket(root_key).add_file(file_path, size_bytes, mtime_ts)
            get_bucket(root_files_key).add_file(file_path, size_bytes, mtime_ts)
            return

        max_bucket_depth = min(max_depth, len(rel_dir_parts))
        for depth in range(0, max_bucket_depth + 1):
            key = _bucket_key_for_dir(root, rel_dir_parts, depth)
            get_bucket(key).add_file(file_path, size_bytes, mtime_ts)

    # Count the root directory itself (helps match expectations when comparing scans)
    try:
        root_stat = root.stat()
        update_dir_buckets(root, root_stat.st_mtime)
    except Exception as e:
        errors.append({"path": str(root), "error": type(e).__name__, "detail": str(e)})

    stack: list[Path] = [root]
    while stack:
        current_dir = stack.pop()
        try:
            with os.scandir(current_dir) as it:
                for entry in it:
                    entry_path = Path(entry.path)
                    try:
                        if entry.is_dir(follow_symlinks=follow_symlinks):
                            stat = entry.stat(follow_symlinks=follow_symlinks)
                            update_dir_buckets(entry_path, stat.st_mtime)
                            if follow_symlinks or not entry.is_symlink():
                                stack.append(entry_path)
                        else:
                            stat = entry.stat(follow_symlinks=follow_symlinks)
                            update_file_buckets(entry_path, stat.st_size, stat.st_mtime)
                    except Exception as e:
                        errors.append(
                            {"path": str(entry_path), "error": type(e).__name__, "detail": str(e)}
                        )
        except Exception as e:
            errors.append({"path": str(current_dir), "error": type(e).__name__, "detail": str(e)})

    # Build entries list (root + depth-1 buckets for readability)
    entries: list[dict[str, object]] = []
    for bucket_path, agg in stats_by_bucket.items():
        if bucket_path == root_files_key:
            entries.append(
                {
                    "bucket_path": bucket_path,
                    "kind": "root_files_bucket",
                    "depth": 1,
                    "classification": "unclassified",
                    "stats": agg.to_json_obj(),
                }
            )
            continue

        rel_parts = _safe_rel_parts(root, Path(bucket_path))
        depth = 0 if bucket_path == root_key else len(rel_parts)
        classification = "unclassified"
        if depth == 1 and rel_parts:
            classification = _classify_top_level_name(rel_parts[0])
        elif depth == 0:
            classification = "root"

        if depth <= max_depth:
            entries.append(
                {
                    "bucket_path": bucket_path,
                    "kind": "directory_bucket",
                    "depth": depth,
                    "classification": classification,
                    "stats": agg.to_json_obj(),
                }
            )

    # Stable ordering: depth, then path
    entries.sort(key=lambda e: (int(e["depth"]), str(e["bucket_path"]).lower()))

    root_stats = stats_by_bucket.get(root_key, AggStats()).to_json_obj()
    return {
        "generated_at_utc": _now_utc_iso(),
        "root": str(root),
        "max_depth": int(max_depth),
        "follow_symlinks": bool(follow_symlinks),
        "root_stats": root_stats,
        "entries": entries,
        "errors": errors,
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a drive inventory JSON report.")
    parser.add_argument(
        "--root",
        type=str,
        default="E:\\",
        help="Root path to scan (default: E:\\\\).",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="Max directory depth for bucketed summaries (default: 2).",
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symlinks when scanning (default: off).",
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
    root = Path(args.root)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    result = scan_drive(root=root, max_depth=args.max_depth, follow_symlinks=args.follow_symlinks)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote inventory: {output}")
    print(f"Root: {result['root']}")
    print(f"Errors: {len(result['errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

