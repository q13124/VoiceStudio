"""
VoiceStudio API Models.

This module defines the core Pydantic models used across the VoiceStudio API.
All models should inherit from VoiceStudioBaseModel to ensure consistent
null handling and serialization behavior.

See: docs/contracts/NULL_HANDLING_POLICY.md for the serialization policy.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

# =============================================================================
# GAP-I16: VoiceStudio Base Model with Standardized Null Handling
# =============================================================================


class VoiceStudioBaseModel(BaseModel):
    """
    Base model with consistent null handling policy (GAP-I16).

    All VoiceStudio API models should inherit from this base to ensure:
    - Null values are omitted from JSON output (matching C# WhenWritingNull)
    - Enums serialize to their values, not names
    - Assignment validation for catching errors early

    Usage:
        class MyModel(VoiceStudioBaseModel):
            field: str
            optional_field: str | None = None
    """

    model_config = ConfigDict(
        # GAP-I16: Omit None values in JSON output (match C# WhenWritingNull)
        # Note: This is enforced at serialization time via model_dump(exclude_none=True)
        # since ConfigDict doesn't have exclude_none - we override model_dump instead
        use_enum_values=True,
        # Validate on assignment for early error detection
        validate_assignment=True,
        # Allow population by field name or alias
        populate_by_name=True,
        # Strip whitespace from strings
        str_strip_whitespace=True,
    )

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """
        Override model_dump to enforce exclude_none=True by default (GAP-I16).

        This ensures null values are consistently omitted from JSON output
        across all models, matching C# JsonSerializerOptions.WhenWritingNull.
        """
        # Set exclude_none=True by default unless explicitly overridden
        if "exclude_none" not in kwargs:
            kwargs["exclude_none"] = True
        return super().model_dump(**kwargs)

    def model_dump_json(self, **kwargs) -> str:
        """
        Override model_dump_json to enforce exclude_none=True by default (GAP-I16).
        """
        if "exclude_none" not in kwargs:
            kwargs["exclude_none"] = True
        return super().model_dump_json(**kwargs)


# =============================================================================
# API Response Models
# =============================================================================


class ApiOk(VoiceStudioBaseModel):
    ok: bool = True


# =============================================================================
# Request Models
# =============================================================================


class TrainRequest(VoiceStudioBaseModel):
    dataset_id: str
    params: dict[str, Any] = {}


class TtsRequest(VoiceStudioBaseModel):
    text: str
    voice_id: str
    prosody: dict[str, Any] | None = None
    style: dict[str, Any] | None = None


class SpectrogramRequest(VoiceStudioBaseModel):
    audio_id: str
    mode: str = "mel"


class LexiconEntry(VoiceStudioBaseModel):
    word: str
    phoneme: str
    locale: str = "en-US"
    scope: str = "project"


class EmbeddingMap(VoiceStudioBaseModel):
    vectors: dict[str, list[float]]


class MixAnalyzeRequest(VoiceStudioBaseModel):
    stems: list[str]
    target: str = "podcast"


class StyleExtractRequest(VoiceStudioBaseModel):
    audio_id: str


class BlendRequest(VoiceStudioBaseModel):
    a_id: str
    b_id: str
    ratio: float = 0.5
    name: str | None = None
