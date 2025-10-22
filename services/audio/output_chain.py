"""
Output Chain Configuration for VoiceStudio Voice Engine Router
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class OutputChain(BaseModel):
    """Optional post-FX steps; all disabled by default (minor-safe)."""
    model_config = ConfigDict(strict=True, extra="forbid")

    trim_ms: int = Field(default=0, ge=0, description="Trim leading/trailing silence by N ms (each side). 0 = disabled.")
    fade_ms: int = Field(default=0, ge=0, description="Apply equal-power fade-in/out of N ms. 0 = disabled.")
    dither: bool = Field(default=False, description="Apply TPDF dither on final write. False = disabled.")

class TTSRequestWithChain(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    text: str = Field(min_length=1)
    language: str | None = None
    profile: str | None = None
    quality: str = Field(default="balanced")
    voice_profile: dict = Field(default_factory=dict)
    params: dict = Field(default_factory=dict)
    
    # Optional output chain
    output_chain: Optional[OutputChain] = Field(default=None, description="Optional audio processing chain")
