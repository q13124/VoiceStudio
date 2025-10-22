
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Dict, Any

@dataclass
class AgentReport:
    name: str
    ok: bool
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)

class Agent(Protocol):
    name: str
    def start(self) -> None: ...
    def report(self) -> AgentReport: ...
    def enqueue(self, item: Dict[str, Any]) -> None: ...
