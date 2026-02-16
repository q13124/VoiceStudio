"""
Health Check System

Provides comprehensive health checking for services, engines, and system components.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)
    response_time_ms: float | None = None
    error: str | None = None


class HealthChecker:
    """
    Health checker for services and components.
    """

    def __init__(self, name: str, timeout: float = 5.0):
        """
        Initialize health checker.

        Args:
            name: Health checker name
            timeout: Timeout for health checks in seconds
        """
        self.name = name
        self.timeout = timeout
        self.checks: dict[str, Callable] = {}
        self.last_results: dict[str, HealthCheckResult] = {}

    def register_check(
        self,
        name: str,
        check_func: Callable,
        critical: bool = True,
    ):
        """
        Register a health check function.

        Args:
            name: Check name
            check_func: Check function (async or sync)
            critical: Whether check is critical
        """
        self.checks[name] = {
            "func": check_func,
            "critical": critical,
        }

    async def run_check(self, name: str) -> HealthCheckResult:
        """
        Run a specific health check.

        Args:
            name: Check name

        Returns:
            Health check result
        """
        if name not in self.checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Check '{name}' not found",
            )

        check_info = self.checks[name]
        check_func = check_info["func"]
        critical = check_info["critical"]

        start_time = time.time()

        try:
            # Run check with timeout
            if asyncio.iscoroutinefunction(check_func):
                result = await asyncio.wait_for(
                    check_func(),
                    timeout=self.timeout
                )
            else:
                # Run sync function in executor
                loop = asyncio.get_event_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, check_func),
                    timeout=self.timeout
                )

            response_time = (time.time() - start_time) * 1000

            # Determine status from result
            if isinstance(result, HealthCheckResult):
                result.response_time_ms = response_time
                status = result.status
            elif isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                result = HealthCheckResult(
                    name=name,
                    status=status,
                    message="Check completed",
                    response_time_ms=response_time,
                )
            elif isinstance(result, dict):
                status = HealthStatus(result.get("status", "unknown"))
                result = HealthCheckResult(
                    name=name,
                    status=status,
                    message=result.get("message", "Check completed"),
                    details=result.get("details", {}),
                    response_time_ms=response_time,
                )
            else:
                status = HealthStatus.HEALTHY
                result = HealthCheckResult(
                    name=name,
                    status=status,
                    message="Check completed",
                    response_time_ms=response_time,
                )

            # Store result
            self.last_results[name] = result
            return result

        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check timed out after {self.timeout}s",
                response_time_ms=response_time,
                error="timeout",
            )
            self.last_results[name] = result
            return result

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            status = HealthStatus.UNHEALTHY if critical else HealthStatus.DEGRADED
            result = HealthCheckResult(
                name=name,
                status=status,
                message=f"Health check failed: {e!s}",
                response_time_ms=response_time,
                error=str(e),
            )
            self.last_results[name] = result
            logger.error(f"Health check '{name}' failed: {e}", exc_info=True)
            return result

    async def run_all_checks(self) -> dict[str, HealthCheckResult]:
        """
        Run all registered health checks.

        Returns:
            Dictionary of check results
        """
        results = {}

        # Run checks in parallel
        tasks = [
            self.run_check(name) for name in self.checks
        ]

        check_results = await asyncio.gather(*tasks, return_exceptions=True)

        for name, result in zip(self.checks.keys(), check_results, strict=False):
            if isinstance(result, Exception):
                results[name] = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed with exception: {result!s}",
                    error=str(result),
                )
            else:
                results[name] = result

        return results

    def get_overall_status(self) -> HealthStatus:
        """
        Get overall health status based on all checks.

        Returns:
            Overall health status
        """
        if not self.last_results:
            return HealthStatus.UNKNOWN

        # Check critical checks first
        critical_failed = False
        any_failed = False

        for name, check_info in self.checks.items():
            if name not in self.last_results:
                continue

            result = self.last_results[name]
            if result.status == HealthStatus.UNHEALTHY:
                any_failed = True
                if check_info["critical"]:
                    critical_failed = True

        if critical_failed:
            return HealthStatus.UNHEALTHY
        elif any_failed:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY


# Global health checker registry
_health_checkers: dict[str, HealthChecker] = {}


def get_health_checker(name: str, timeout: float = 5.0) -> HealthChecker:
    """
    Get or create a health checker.

    Args:
        name: Health checker name
        timeout: Timeout for checks

    Returns:
        Health checker instance
    """
    if name not in _health_checkers:
        _health_checkers[name] = HealthChecker(name=name, timeout=timeout)
    return _health_checkers[name]


def create_simple_check(
    name: str,
    check_func: Callable,
    critical: bool = True,
) -> HealthCheckResult:
    """
    Create a simple health check result.

    Args:
        name: Check name
        check_func: Check function
        critical: Whether check is critical

    Returns:
        Health check result
    """
    try:
        if asyncio.iscoroutinefunction(check_func):
            # For async, need to run in event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(check_func())
        else:
            result = check_func()

        if isinstance(result, bool):
            status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
            return HealthCheckResult(
                name=name,
                status=status,
                message="Check completed",
            )
        else:
            return result

    except Exception as e:
        status = HealthStatus.UNHEALTHY if critical else HealthStatus.DEGRADED
        return HealthCheckResult(
            name=name,
            status=status,
            message=f"Check failed: {e!s}",
            error=str(e),
        )

