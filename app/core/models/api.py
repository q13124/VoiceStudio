from typing import Annotated
from pydantic import Field, PlainSerializer, WithJsonSchema
from .base import StrictModel

# Lightweight constrained strings (minor-safe: keep type=str at runtime)
Lang = Annotated[
    str,
    Field(min_length=2, max_length=10, description="BCP-47 like tag (e.g., 'en', 'en-US')"),
]
ProfileId = Annotated[
    str,
    Field(min_length=1, max_length=128, description="Voice/profile identifier"),
]

class Problem(StrictModel):
    type: str = Field(default="about:blank", description="RFC 7807 problem type")
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
