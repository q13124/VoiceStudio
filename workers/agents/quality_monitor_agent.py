
from __future__ import annotations
from core.api.protocols.agents import AgentReport

class QualityMonitorAgent:
    name = "quality_monitor"
    def start(self) -> None:
        pass
    def report(self) -> AgentReport:
        return AgentReport(name=self.name, ok=True, summary="Objective checks idle", details={"lufs": None, "clipping": None})
    def enqueue(self, item):
        pass
