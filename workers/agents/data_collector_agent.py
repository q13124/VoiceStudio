
from __future__ import annotations
from core.api.protocols.agents import AgentReport

class DataCollectorAgent:
    name = "data_collector"
    def start(self) -> None:
        pass
    def report(self) -> AgentReport:
        return AgentReport(name=self.name, ok=True, summary="No new datasets")
    def enqueue(self, item):
        pass
