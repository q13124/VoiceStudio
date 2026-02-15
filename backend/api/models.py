
from __future__ import annotations
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ApiOk(BaseModel):
    ok: bool = True

class TrainRequest(BaseModel):
    dataset_id: str
    params: Dict[str, Any] = {}

class TtsRequest(BaseModel):
    text: str
    voice_id: str
    prosody: Optional[Dict[str, Any]] = None
    style: Optional[Dict[str, Any]] = None

class SpectrogramRequest(BaseModel):
    audio_id: str
    mode: str = "mel"

class LexiconEntry(BaseModel):
    word: str
    phoneme: str
    locale: str = "en-US"
    scope: str = "project"

class EmbeddingMap(BaseModel):
    vectors: Dict[str, List[float]]

class MixAnalyzeRequest(BaseModel):
    stems: List[str]
    target: str = "podcast"

class StyleExtractRequest(BaseModel):
    audio_id: str

class BlendRequest(BaseModel):
    a_id: str
    b_id: str
    ratio: float = 0.5
    name: Optional[str] = None

