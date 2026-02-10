"""
Synthesis Commands.

Task 3.2.1: Commands for voice synthesis operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from backend.application.commands.base import Command


@dataclass
class SynthesizeSpeech(Command):
    """Command to synthesize speech from text."""
    
    text: str = ""
    voice_profile_id: str = ""
    project_id: Optional[str] = None
    language: str = "en"
    
    # Audio settings
    sample_rate: int = 22050
    format: str = "wav"
    
    # Voice adjustments
    speed: float = 1.0
    pitch: float = 0.0
    
    # Engine selection
    engine_id: Optional[str] = None
    
    # Output
    output_path: Optional[str] = None


@dataclass
class ProcessAudioClip(Command):
    """Command to process an audio clip."""
    
    clip_id: str = ""
    
    # Processing options
    normalize: bool = True
    remove_silence: bool = False
    add_reverb: bool = False
    
    # Speed/pitch adjustment
    speed: float = 1.0
    pitch: float = 0.0


@dataclass
class CloneVoice(Command):
    """Command to clone a voice from samples."""
    
    name: str = ""
    sample_paths: list = field(default_factory=list)
    language: str = "en"
    description: str = ""
    
    # Engine selection
    engine_id: Optional[str] = None


@dataclass
class BatchSynthesize(Command):
    """Command to synthesize multiple texts."""
    
    texts: list = field(default_factory=list)
    voice_profile_id: str = ""
    project_id: Optional[str] = None
    
    # Settings applied to all
    language: str = "en"
    engine_id: Optional[str] = None


@dataclass
class CancelSynthesis(Command):
    """Command to cancel ongoing synthesis."""
    
    job_id: str = ""
    force: bool = False
