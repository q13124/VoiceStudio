#!/usr/bin/env python3
# Copyright (c) VoiceStudio. All rights reserved.
# Licensed under the MIT License.

"""
Standard path setup for VoiceStudio scripts.

IMPORTANT: Import this module FIRST in every script that needs access to
VoiceStudio packages (app, backend, tools, etc.).

Usage:
    from _env_setup import PROJECT_ROOT

This module:
- Adds the project root to sys.path
- Sets up the Python path for all VoiceStudio modules
- Provides PROJECT_ROOT as a Path object for file operations

Example:
    #!/usr/bin/env python3
    from _env_setup import PROJECT_ROOT
    
    from app.core.engines import router
    from tools.context import ContextManager
"""

import sys
from pathlib import Path

# Calculate project root (parent of the scripts directory)
_PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Add project root to sys.path if not already there
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Export for use in scripts
PROJECT_ROOT = _PROJECT_ROOT

# Common directories
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
BACKEND_DIR = PROJECT_ROOT / "backend"
APP_DIR = PROJECT_ROOT / "app"
TOOLS_DIR = PROJECT_ROOT / "tools"
TESTS_DIR = PROJECT_ROOT / "tests"
DOCS_DIR = PROJECT_ROOT / "docs"
SRC_DIR = PROJECT_ROOT / "src"

# Buildlog directories
BUILDLOGS_DIR = PROJECT_ROOT / ".buildlogs"
VERIFICATION_DIR = BUILDLOGS_DIR / "verification"

# Ensure buildlog directories exist
BUILDLOGS_DIR.mkdir(exist_ok=True)
VERIFICATION_DIR.mkdir(exist_ok=True)

__all__ = [
    "PROJECT_ROOT",
    "SCRIPTS_DIR",
    "BACKEND_DIR",
    "APP_DIR",
    "TOOLS_DIR",
    "TESTS_DIR",
    "DOCS_DIR",
    "SRC_DIR",
    "BUILDLOGS_DIR",
    "VERIFICATION_DIR",
]
