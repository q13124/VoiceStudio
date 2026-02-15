"""
Context Accumulation Cost Tracker for VoiceStudio (Phase 10.3.2)

Tracks cumulative costs across S2S sessions and provides analytics
on usage patterns for cost optimization.
"""

from __future__ import annotations

import json
import logging
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SessionCostEntry:
    """Cost record for a completed session."""
    session_id: str
    provider: str
    total_tokens: int
    turn_count: int
    duration_seconds: float
    estimated_cost_usd: float
    ceiling_triggered: bool
    timestamp: float


class CostTracker:
    """
    Tracks cumulative costs across S2S sessions.

    Persists cost data locally for analytics and reporting.
    """

    def __init__(self, data_dir: str | None = None, max_history: int = 1000):
        self._data_dir = Path(data_dir or "~/.voicestudio/costs").expanduser()
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._history: deque[SessionCostEntry] = deque(maxlen=max_history)
        self._total_spent: float = 0.0
        self._load_history()

    def record_session(self, entry: SessionCostEntry) -> None:
        """Record a completed session's cost."""
        self._history.append(entry)
        self._total_spent += entry.estimated_cost_usd
        self._save_entry(entry)
        logger.info(
            f"Cost recorded: session={entry.session_id}, "
            f"cost=${entry.estimated_cost_usd:.4f}, "
            f"total=${self._total_spent:.4f}"
        )

    def get_summary(self) -> dict[str, Any]:
        """Get cost summary across all sessions."""
        if not self._history:
            return {
                "total_sessions": 0,
                "total_cost_usd": 0.0,
                "avg_cost_per_session": 0.0,
            }

        costs = [e.estimated_cost_usd for e in self._history]
        durations = [e.duration_seconds for e in self._history]
        tokens = [e.total_tokens for e in self._history]

        return {
            "total_sessions": len(self._history),
            "total_cost_usd": round(sum(costs), 4),
            "avg_cost_per_session": round(sum(costs) / len(costs), 4),
            "avg_duration_seconds": round(sum(durations) / len(durations), 1),
            "avg_tokens_per_session": round(sum(tokens) / len(tokens)),
            "ceiling_trigger_rate": round(
                sum(1 for e in self._history if e.ceiling_triggered) / len(self._history), 2
            ),
            "by_provider": self._group_by_provider(),
        }

    def _group_by_provider(self) -> dict[str, dict[str, Any]]:
        """Group costs by provider."""
        providers: dict[str, list[SessionCostEntry]] = {}
        for entry in self._history:
            providers.setdefault(entry.provider, []).append(entry)

        result = {}
        for provider, entries in providers.items():
            costs = [e.estimated_cost_usd for e in entries]
            result[provider] = {
                "sessions": len(entries),
                "total_cost_usd": round(sum(costs), 4),
                "avg_cost_usd": round(sum(costs) / len(costs), 4),
            }
        return result

    def _save_entry(self, entry: SessionCostEntry) -> None:
        """Persist cost entry to disk."""
        try:
            cost_file = self._data_dir / "cost_history.jsonl"
            data = {
                "session_id": entry.session_id,
                "provider": entry.provider,
                "total_tokens": entry.total_tokens,
                "turn_count": entry.turn_count,
                "duration_seconds": entry.duration_seconds,
                "estimated_cost_usd": entry.estimated_cost_usd,
                "ceiling_triggered": entry.ceiling_triggered,
                "timestamp": entry.timestamp,
            }
            with open(cost_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
        except Exception as exc:
            logger.warning(f"Failed to save cost entry: {exc}")

    def _load_history(self) -> None:
        """Load cost history from disk."""
        cost_file = self._data_dir / "cost_history.jsonl"
        if not cost_file.exists():
            return
        try:
            with open(cost_file, encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        entry = SessionCostEntry(**data)
                        self._history.append(entry)
                        self._total_spent += entry.estimated_cost_usd
                    except (json.JSONDecodeError, TypeError):
                        continue
        except Exception as exc:
            logger.warning(f"Failed to load cost history: {exc}")
