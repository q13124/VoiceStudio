from pydantic import BaseModel, ConfigDict, Field

class OutputChain(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    trim_ms: int = Field(default=0, ge=0, description="Trim silence from start/end in milliseconds")
    fade_ms: int = Field(default=0, ge=0, description="Fade in/out duration in milliseconds")
    dither: bool = Field(default=False, description="Apply dithering to reduce quantization noise")
