
from __future__ import annotations
from core.api.protocols.agents import AgentReport

class PerformanceAgent:
    name = "performance"
    def start(self) -> None:
        pass
    def report(self) -> AgentReport:
        return AgentReport(name=self.name, ok=True, summary="GPU/VRAM snapshot queued", details={})
    def enqueue(self, item):
        pass
