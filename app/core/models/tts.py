from pydantic import Field
from app.core.models.base import StrictModel
from app.core.models.api import Lang, ProfileId
from services.models.output_chain import OutputChain
from services.models.audio_metrics import AudioMetrics


class TTSRequest(StrictModel):
    text: str = Field(min_length=1, description="Input text to synthesize")

    # Keep language/profile flexible (additive, optional)
    language: Lang | None = None
    profile: ProfileId | None = None

    output_chain: OutputChain | None = None

    # Example of a deprecated alias (additive, NOT removed)
    # 'voice' used to be the profile id; keep it for backward compatibility:
    voice: str | None = Field(
        default=None,
        json_schema_extra={
            "deprecated": True,
            "description": "Deprecated; use 'profile'",
        },
    )


class TTSItem(StrictModel):
    id: str
    engine: str
    url: str
    metrics: AudioMetrics | None = None


class TTSResponse(StrictModel):
    items: list[TTSItem]
