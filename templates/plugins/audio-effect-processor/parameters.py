"""Typed parameter models for the audio effect processor template."""

from pydantic import BaseModel, Field


class EffectParameters(BaseModel):
    """Validated parameters for processor behavior."""

    gain_db: float = Field(default=0.0, ge=-24.0, le=24.0)
    normalize_output: bool = Field(default=True)
    target_peak: float = Field(default=0.98, gt=0.0, le=1.0)
