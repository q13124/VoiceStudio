"""Backend process supervisor module for high-availability."""

from backend.supervisor.watchdog import ProcessWatchdog, WatchdogConfig

__all__ = ["ProcessWatchdog", "WatchdogConfig"]
