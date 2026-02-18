"""
VoiceStudio Plugin CLI Commands.

Subcommand modules for the plugin CLI:
- init: Initialize new plugin projects
- validate: Validate plugin manifests
- test: Run plugin tests
- pack: Package plugins into .vspkg format
- sign: Sign plugin packages
- publish: Publish to the catalog
- certify: Run automated certification with quality gates (Phase 5C M3)
- lock: Lockfile management for version pinning (Phase 5C M4)
- benchmark: Performance benchmarking with standardized test suite (Phase 5D M1)
"""

from . import benchmark, certify, init, lock, pack, publish, sign, test, validate

__all__ = [
    "benchmark",
    "certify",
    "init",
    "lock",
    "pack",
    "publish",
    "sign",
    "test",
    "validate",
]
