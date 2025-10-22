from pydantic import Field
from app.core.models.base import StrictModel

class AudioMetrics(StrictModel):
    lufs: float | None = Field(default=None, description="Integrated loudness (I, dB)")
    lra: float | None = Field(default=None, description="Loudness range (dB)")
    true_peak: float | None = Field(default=None, description="True peak (dBTP)")
    clip_pct: float | None = Field(default=None, ge=0.0, le=100.0, description="% of clipped samples (approx or derived)")
    dc_offset: float | None = Field(default=None, ge=0.0, description="DC offset %FS")
    head_ms: int | None = Field(default=None, ge=0, description="Leading silence (ms)")
    tail_ms: int | None = Field(default=None, ge=0, description="Trailing silence (ms)")
