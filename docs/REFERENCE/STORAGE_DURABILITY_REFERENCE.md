# Storage Durability Reference

**Domain:** Core Platform (Role 4)
**Created:** 2026-02-10
**Status:** Active

## Overview

This document describes VoiceStudio's storage durability guarantees and atomic-write patterns.

## Storage Locations

| Location | Purpose | Durability |
|----------|---------|------------|
| `data/profiles/` | Voice profiles | Atomic JSON writes |
| `data/projects/` | Project files | Atomic with backup |
| `data/jobs/` | Job state | Transient, recoverable |
| `data/models/` | Trained models | Immutable after creation |

## Atomic Write Pattern

All configuration and state files use atomic write operations:

```python
# Pattern used in JobStateStore, ProfileStore, etc.
def atomic_write(path: Path, data: bytes) -> None:
    temp_path = path.with_suffix('.tmp')
    temp_path.write_bytes(data)
    temp_path.replace(path)  # Atomic on POSIX/Windows
```

## Backup Strategy

- Automatic backups before destructive operations
- Backup location: `data/backups/`
- Retention: 7 days default

## Recovery

- Corrupted JSON files: Restore from `.bak` suffix files
- Missing state: Rebuild from job logs
- Model corruption: Re-download from cache

## Related Documents

- [Preflight Reference](PREFLIGHT_REFERENCE.md)
- [Job Runtime Map Reference](JOB_RUNTIME_MAP_REFERENCE.md)
