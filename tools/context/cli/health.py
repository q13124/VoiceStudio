#!/usr/bin/env python3
"""
Context Source Health Check CLI.

Checks the health of all context sources and displays telemetry data.

Usage:
    python -m tools.context.cli.health          # Check all sources
    python -m tools.context.cli.health --json   # Output as JSON
    python -m tools.context.cli.health --test   # Run a test allocation
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.context.core.manager import ContextManager
from tools.context.core.models import AllocationContext, ContextLevel


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def check_health(manager: ContextManager, output_json: bool = False) -> dict:
    """Check health of all context sources."""
    health = manager.health_check()

    if output_json:
        print(json.dumps(health, indent=2))
    else:
        print("\n" + "=" * 60)
        print("  CONTEXT SOURCE HEALTH CHECK")
        print("=" * 60 + "\n")

        overall = "HEALTHY" if health["overall_healthy"] else "UNHEALTHY"
        color = "\033[92m" if health["overall_healthy"] else "\033[91m"
        reset = "\033[0m"

        print(f"Overall Status: {color}{overall}{reset}")
        print(f"Healthy: {health['healthy_count']}/{health['total_count']}")
        print(f"Timestamp: {health['timestamp']}")
        print()

        if health["unhealthy_sources"]:
            print("Unhealthy Sources:")
            for source in health["unhealthy_sources"]:
                print(f"  - {source}")
            print()

        print("Source Details:")
        print("-" * 60)

        for source in health["sources"]:
            status = source.get("status", {})
            healthy = source.get("healthy", False)
            icon = "✓" if healthy else "✗"
            color = "\033[92m" if healthy else "\033[91m"

            print(f"\n{color}{icon}{reset} {source['source']}")
            if status:
                print(f"    Total fetches: {status.get('total_fetches', 0)}")
                print(f"    Failure rate: {status.get('failure_rate', 0)}%")
                print(f"    Avg fetch time: {status.get('avg_fetch_time_ms', 0):.1f}ms")
                if status.get("last_error"):
                    print(f"    Last error: {status['last_error'][:80]}")

    return health


def run_test_allocation(manager: ContextManager) -> dict:
    """Run a test allocation to exercise all sources."""
    print("\nRunning test allocation...")

    context = AllocationContext(
        task_id="HEALTH-CHECK",
        phase="test",
        role=None,
        include_git=True,
        budget_chars=12000,
        max_level=ContextLevel.LOW,
    )

    try:
        bundle = manager.allocate(context)
        telemetry = manager.get_telemetry_summary()

        print(f"  Bundle generated: {len(bundle.to_json())} chars")
        print(f"  Sources contacted: {telemetry.get('total_sources', 0)}")
        print(f"  Healthy sources: {telemetry.get('healthy_sources', 0)}")

        return {
            "success": True,
            "bundle_size": len(bundle.to_json()),
            "telemetry": telemetry,
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        return {
            "success": False,
            "error": str(e),
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check health of context sources"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run a test allocation to exercise sources",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config file",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    try:
        if args.config:
            manager = ContextManager.from_config(args.config)
        else:
            manager = ContextManager.from_config()
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "success": False}))
        else:
            print(f"ERROR: Failed to initialize context manager: {e}")
        return 1

    # Run health check
    health = check_health(manager, output_json=args.json)

    # Optionally run test allocation
    if args.test and not args.json:
        run_test_allocation(manager)

    # Return exit code based on health
    return 0 if health.get("overall_healthy", False) else 1


if __name__ == "__main__":
    sys.exit(main())
