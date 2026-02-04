#!/usr/bin/env python3
"""
Context Manager Health Monitor.

Autonomous monitoring script that periodically checks the health
of the context manager and its adapters. Logs failures to the
audit system for Debug Role visibility.

Can be run as:
- One-shot health check: python scripts/context_manager_health.py
- Continuous monitoring: python scripts/context_manager_health.py --watch
"""

from _env_setup import PROJECT_ROOT

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ContextManagerHealthMonitor:
    """
    Monitors context manager health and reports issues.
    
    Performs periodic health checks on:
    - Configuration validity
    - Source adapter availability
    - Allocation performance
    - Audit system integration
    """
    
    # Performance thresholds (milliseconds)
    ALLOCATION_WARN_MS = 500
    ALLOCATION_ERROR_MS = 2000
    ADAPTER_WARN_MS = 100
    ADAPTER_ERROR_MS = 500
    
    def __init__(
        self,
        check_interval_seconds: int = 60,
        log_to_audit: bool = True,
    ):
        """
        Initialize the health monitor.
        
        Args:
            check_interval_seconds: Seconds between health checks
            log_to_audit: Whether to log issues to audit system
        """
        self._interval = check_interval_seconds
        self._log_to_audit = log_to_audit
        self._last_check: Optional[datetime] = None
        self._health_history: List[Dict[str, Any]] = []
        self._audit_logger = None
    
    def _init_audit_logger(self):
        """Initialize audit logger for reporting."""
        if not self._log_to_audit:
            return
        
        try:
            from app.core.audit import get_audit_logger
            self._audit_logger = get_audit_logger()
        except ImportError:
            self._audit_logger = None
    
    def check_adapter_health(self, adapter_name: str) -> Dict[str, Any]:
        """Check health of a specific adapter."""
        result = {
            "name": adapter_name,
            "status": "unknown",
            "latency_ms": 0.0,
            "error": None,
        }
        
        try:
            from tools.context.core.models import AllocationContext, ContextLevel
            
            # Import the specific adapter
            module_map = {
                "state": ("tools.context.sources.state_adapter", "StateSourceAdapter"),
                "task": ("tools.context.sources.task_adapter", "TaskSourceAdapter"),
                "rules": ("tools.context.sources.rules_adapter", "RulesSourceAdapter"),
                "memory": ("tools.context.sources.memory_adapter", "MemorySourceAdapter"),
                "git": ("tools.context.sources.git_adapter", "GitSourceAdapter"),
                "ledger": ("tools.context.sources.ledger_adapter", "LedgerSourceAdapter"),
                "issues": ("tools.context.sources.issues_adapter", "IssuesSourceAdapter"),
                "audit": ("tools.context.sources.audit_adapter", "AuditSourceAdapter"),
            }
            
            if adapter_name not in module_map:
                result["status"] = "unknown"
                result["error"] = f"Unknown adapter: {adapter_name}"
                return result
            
            module_path, class_name = module_map[adapter_name]
            module = __import__(module_path, fromlist=[class_name])
            adapter_class = getattr(module, class_name)
            
            # Instantiate and test
            start = time.perf_counter()
            adapter = adapter_class()
            
            context = AllocationContext(
                task_id="HEALTH-CHECK",
                phase="Monitor",
                role="system",
                include_git=False,
                budget_chars=1000,
                max_level=ContextLevel.LOW,
            )
            
            fetch_result = adapter.fetch(context)
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            result["latency_ms"] = round(elapsed_ms, 2)
            
            if not fetch_result.success:
                result["status"] = "error"
                result["error"] = fetch_result.error
            elif elapsed_ms > self.ADAPTER_ERROR_MS:
                result["status"] = "slow"
                result["error"] = f"Latency {elapsed_ms:.0f}ms exceeds threshold {self.ADAPTER_ERROR_MS}ms"
            elif elapsed_ms > self.ADAPTER_WARN_MS:
                result["status"] = "degraded"
            else:
                result["status"] = "healthy"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def check_allocation_health(self) -> Dict[str, Any]:
        """Check overall allocation health."""
        result = {
            "status": "unknown",
            "latency_ms": 0.0,
            "sources_ok": 0,
            "sources_failed": 0,
            "total_chars": 0,
            "error": None,
        }
        
        try:
            from tools.context.core.manager import ContextManager
            from tools.context.core.models import AllocationContext, ContextLevel
            
            start = time.perf_counter()
            
            manager = ContextManager.from_config()
            
            context = AllocationContext(
                task_id="HEALTH-CHECK",
                phase="Monitor",
                role="debug-agent",
                include_git=False,
                budget_chars=5000,
                max_level=ContextLevel.MID,
            )
            
            bundle = manager.allocate(context)
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            result["latency_ms"] = round(elapsed_ms, 2)
            
            # Count sources present in bundle
            sources_present = 0
            if bundle.task and bundle.task.id is not None:
                sources_present += 1
            if bundle.state and bundle.state.phase is not None:
                sources_present += 1
            if bundle.brief:
                sources_present += 1
            if bundle.rules:
                sources_present += 1
            if bundle.memory:
                sources_present += 1
            if bundle.git:
                sources_present += 1
            if bundle.ledger:
                sources_present += 1
            
            result["sources_ok"] = sources_present
            result["total_chars"] = len(bundle.to_json())
            
            if result["total_chars"] < 100:
                result["status"] = "error"
                result["error"] = "Allocation returned minimal content"
            elif elapsed_ms > self.ALLOCATION_ERROR_MS:
                result["status"] = "slow"
                result["error"] = f"Latency {elapsed_ms:.0f}ms exceeds threshold {self.ALLOCATION_ERROR_MS}ms"
            elif elapsed_ms > self.ALLOCATION_WARN_MS:
                result["status"] = "degraded"
            else:
                result["status"] = "healthy"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run a complete health check."""
        timestamp = datetime.now(timezone.utc)
        
        check_result = {
            "timestamp": timestamp.isoformat(),
            "overall_status": "unknown",
            "allocation": {},
            "adapters": {},
            "issues": [],
        }
        
        # Check allocation health
        allocation = self.check_allocation_health()
        check_result["allocation"] = allocation
        
        # Check individual adapters
        adapter_names = ["state", "task", "rules", "memory", "git", "ledger", "audit"]
        for name in adapter_names:
            adapter_result = self.check_adapter_health(name)
            check_result["adapters"][name] = adapter_result
            
            if adapter_result["status"] == "error":
                check_result["issues"].append(f"Adapter {name}: {adapter_result['error']}")
        
        # Determine overall status
        if allocation["status"] == "error":
            check_result["overall_status"] = "unhealthy"
        elif allocation["status"] in ["slow", "degraded"]:
            check_result["overall_status"] = "degraded"
        elif any(a["status"] == "error" for a in check_result["adapters"].values()):
            check_result["overall_status"] = "degraded"
        else:
            check_result["overall_status"] = "healthy"
        
        # Log to audit if issues found
        if check_result["issues"] and self._audit_logger:
            self._log_health_issue(check_result)
        
        # Store in history
        self._health_history.append(check_result)
        if len(self._health_history) > 100:
            self._health_history = self._health_history[-100:]
        
        self._last_check = timestamp
        
        return check_result
    
    def _log_health_issue(self, check_result: Dict[str, Any]):
        """Log health issues to audit system."""
        if not self._audit_logger:
            return
        
        try:
            from app.core.audit.schema import AuditEntry, AuditEventType
            
            entry = AuditEntry(
                event_type="context_manager_health",
                severity="warning" if check_result["overall_status"] == "degraded" else "error",
                subsystem="context-manager",
                summary=f"Context manager health: {check_result['overall_status']}",
                message="; ".join(check_result["issues"]),
                extra={
                    "allocation_latency_ms": check_result["allocation"]["latency_ms"],
                    "sources_ok": check_result["allocation"]["sources_ok"],
                    "sources_failed": check_result["allocation"]["sources_failed"],
                },
            )
            
            # Write directly to audit log
            self._audit_logger._write_entry(entry)
            
        except Exception:
            # Don't let audit logging failures break health monitoring
            pass
    
    def get_status_summary(self) -> str:
        """Get a human-readable status summary."""
        if not self._health_history:
            return "No health checks run yet"
        
        latest = self._health_history[-1]
        
        lines = [
            f"Status: {latest['overall_status'].upper()}",
            f"Timestamp: {latest['timestamp']}",
            f"Allocation: {latest['allocation']['status']} ({latest['allocation']['latency_ms']}ms)",
            f"Sources OK: {latest['allocation']['sources_ok']}",
            f"Sources Failed: {latest['allocation']['sources_failed']}",
        ]
        
        if latest["issues"]:
            lines.append(f"Issues: {len(latest['issues'])}")
            for issue in latest["issues"][:5]:
                lines.append(f"  - {issue}")
        
        return "\n".join(lines)
    
    def watch(self, max_iterations: Optional[int] = None):
        """
        Continuously monitor health.
        
        Args:
            max_iterations: Maximum number of checks (None for infinite)
        """
        self._init_audit_logger()
        
        iteration = 0
        try:
            while max_iterations is None or iteration < max_iterations:
                iteration += 1
                
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Health check #{iteration}")
                print("-" * 40)
                
                result = self.run_health_check()
                print(self.get_status_summary())
                
                if max_iterations is None or iteration < max_iterations:
                    time.sleep(self._interval)
                    
        except KeyboardInterrupt:
            print("\nHealth monitoring stopped")
    
    def save_report(self, output_path: Optional[Path] = None) -> Path:
        """Save health report to file."""
        if output_path is None:
            output_path = Path(".buildlogs/verification/context_manager_health.json")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "latest_check": self._health_history[-1] if self._health_history else None,
            "history_count": len(self._health_history),
            "recent_history": self._health_history[-10:],
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        
        return output_path


def main():
    """Run context manager health monitoring."""
    parser = argparse.ArgumentParser(
        description="Context Manager Health Monitor"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously monitor health",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Seconds between health checks (default: 60)",
    )
    parser.add_argument(
        "--no-audit",
        action="store_true",
        help="Disable audit logging of issues",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON",
    )
    
    args = parser.parse_args()
    
    monitor = ContextManagerHealthMonitor(
        check_interval_seconds=args.interval,
        log_to_audit=not args.no_audit,
    )
    
    if args.watch:
        monitor.watch()
    else:
        result = monitor.run_health_check()
        
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(monitor.get_status_summary())
        
        # Save report
        report_path = monitor.save_report()
        print(f"\nReport saved to: {report_path}")
        
        # Exit code based on status
        if result["overall_status"] == "healthy":
            return 0
        elif result["overall_status"] == "degraded":
            return 1
        else:
            return 2


if __name__ == "__main__":
    sys.exit(main())
