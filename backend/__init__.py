"""
VoiceStudio Backend Package.

Contains the FastAPI backend API, services, and configuration.
"""

# Import subpackages to make them accessible as backend.services, etc.
from . import services

__all__ = ["services"]
