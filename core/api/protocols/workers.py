
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Dict, Any

@dataclass
class Health:
    healthy: bool
    message: str = ""

class Worker(Protocol):
    name: str
    def process(self, job: Dict[str, Any]) -> Dict[str, Any]: ...
    def health(self) -> Health: ...
