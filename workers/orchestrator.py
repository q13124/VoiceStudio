
from __future__ import annotations
import argparse, time, json
from services.telemetry.metrics import metrics
from services.telemetry import events
from services.overseer.emit_report import emit_report

from workers.agents.quality_monitor_agent import QualityMonitorAgent
from workers.agents.performance_agent import PerformanceAgent
from workers.agents.training_agent import TrainingAgent
from workers.agents.data_collector_agent import DataCollectorAgent
from workers.agents.ab_testing_agent import ABTestingAgent

AGENTS = [
    QualityMonitorAgent(),
    PerformanceAgent(),
    TrainingAgent(),
    DataCollectorAgent(),
    ABTestingAgent(),
]

def step_once():
    for a in AGENTS:
        try:
            a.start()
            r = a.report()
            events.emit({"agent": a.name, "ok": r.ok, "summary": r.summary})
        except Exception as e:
            events.emit({"agent": getattr(a, "name", "unknown"), "ok": False, "error": str(e)})
    metrics.inc("cycles", 1)
    return emit_report()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="Run a single cycle and exit")
    args = ap.parse_args()
    if args.once:
        rep = step_once()
        print(json.dumps(rep, indent=2))
    else:
        while True:
            rep = step_once()
            print(json.dumps(rep))
            time.sleep(15 * 60)

if __name__ == "__main__":
    main()
