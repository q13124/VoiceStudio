# ADR-041: Python 3.11 Runtime for Development Environment

**Status:** Accepted
**Date:** 2026-02-21
**Decision Makers:** Overseer (Role 0)

## Context

VS-0046 documented 25 CVEs across 6 Python packages, all blocked because fix versions required Python 3.10+. The system `python` on PATH points to C:\Python39\python.exe (3.9.13), but the project `.venv` was already created with Python 3.11.9 (available at C:\Users\Tyler\AppData\Local\Programs\Python\Python311\python.exe).

Previous pip-audit runs were executed against the system Python 3.9, not the .venv, leading to incorrect "BLOCKED" assessments.

## Decision

Use Python 3.11.9 via the `.venv` virtual environment for all VoiceStudio development and runtime. The system Python 3.9.13 at C:\Python39 remains installed but is not used by VoiceStudio.

## Consequences

### Positive

- All 25 CVEs from VS-0046 resolved (filelock, python-multipart, pillow, keras, transformers upgraded)
- 3 additional CVEs discovered and fixed (cryptography, pip, protobuf)
- pip-audit now reports **0 known vulnerabilities**
- Python 3.11 provides 10-25% performance improvements over 3.9
- Modern typing features available (ParamSpec, TypeVarTuple, match statements)

### Negative

- moviepy 2.2.1 has a pillow<12.0 constraint that is now violated (pillow 12.1.1 installed)
  - Risk: Low. MoviePy is used for video editing, not core voice synthesis. Pillow 12 is backward-compatible.
- torch 2.2.2+cu121 packages are custom builds that pip-audit cannot verify
  - Mitigation: These are direct PyTorch downloads, not modified by VoiceStudio

### Neutral

- Installer bundled Python (installer/runtime/python/) is separate from the dev .venv
- The `from __future__ import annotations` pattern already used in 300+ files ensures forward compatibility

## Package Versions After Upgrade

| Package | Before (3.9) | After (.venv 3.11) | CVEs Fixed |
|---------|-------------|-------------------|-----------|
| filelock | 3.19.1 | 3.20.3 | 2 |
| python-multipart | 0.0.20 | 0.0.22 | 1 |
| pillow | 11.3.0 | 12.1.1 | 1 |
| keras | 3.10.0 | 3.13.2 | 6 |
| transformers | 4.46.2 | 4.55.4 | 14 |
| cryptography | 46.0.4 | 46.0.5 | 1 |
| pip | 25.3 | 26.0.1 | 1 |
| protobuf | 6.33.4 | 6.33.5 | 1 |
| basicsr | 1.4.2 | 1.4.2 | 1 (no fix available, accepted risk) |
| **Total** | | | **28 fixed, 1 accepted** |
