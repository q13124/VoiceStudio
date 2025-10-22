
from __future__ import annotations
from core.api.protocols.agents import AgentReport

class ABTestingAgent:
    name = "ab_testing"
    def start(self) -> None:
        pass
    def report(self) -> AgentReport:
        return AgentReport(name=self.name, ok=True, summary="No active experiments")
    def enqueue(self, item):
        pass
