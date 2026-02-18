"""Audio effect models."""

from typing import List

from pydantic import BaseModel, Field


class ProcessAudioRequest(BaseModel):
    """Request model for audio effect processing."""

    samples: List[float] = Field(..., description="Audio samples in -1.0..1.0 range")
    sample_rate: int = Field(..., gt=0, description="Sample rate in Hz")
    gain_db: float = Field(default=0.0, description="Gain in dB")


class ProcessAudioResponse(BaseModel):
    """Response model for processed audio."""

    samples: List[float]
    sample_rate: int
    duration_ms: float
