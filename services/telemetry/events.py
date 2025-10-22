
from __future__ import annotations
import json, time, os
from typing import Dict, Any

LOG_PATH = os.environ.get("VS_EVENT_LOG", "telemetry_events.jsonl")

def emit(event: Dict[str, Any]) -> None:
    event = {"ts": time.time(), **event}
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
