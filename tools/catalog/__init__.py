"""
VoiceStudio Plugin Catalog Tools

This package provides tools for managing the VoiceStudio plugin catalog:

- parse_submission.py: Parse plugin submissions from GitHub issues
- validate_submission.py: Validate plugin manifests against schema
- security_scan.py: Perform security analysis on plugin code
- add_to_catalog.py: Add approved plugins to the catalog

These tools are used by GitHub Actions workflows to automate the
plugin submission and approval process.
"""

__version__ = "1.0.0"
