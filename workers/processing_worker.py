
from __future__ import annotations
from core.api.protocols.workers import Health

class ProcessingWorker:
    name = "processing"
    def process(self, job):
        return {"status": "ok", "job": job}
    def health(self) -> Health:
        return Health(healthy=True, message="ok")
