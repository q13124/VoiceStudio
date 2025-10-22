
from __future__ import annotations
from core.api.protocols.agents import AgentReport

class TrainingAgent:
    name = "training"
    def start(self) -> None:
        pass
    def report(self) -> AgentReport:
        return AgentReport(name=self.name, ok=True, summary="No training jobs")
    def enqueue(self, item):
        pass
