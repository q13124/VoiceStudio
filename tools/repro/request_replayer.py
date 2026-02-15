"""
Request Replayer

Replays recorded HTTP sessions for debugging and regression testing.
"""

import argparse
import gzip
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ReplayResult:
    """Result of replaying a request."""

    request_index: int
    method: str
    path: str
    expected_status: int
    actual_status: int
    status_match: bool
    response_time_ms: float
    error: str | None = None


@dataclass
class SessionReplayReport:
    """Report from replaying a session."""

    session_id: str
    total_requests: int
    successful_replays: int
    failed_replays: int
    status_mismatches: int
    results: list[ReplayResult]
    total_time_ms: float


def load_session(session_path: Path) -> dict[str, Any]:
    """Load a recorded session from file."""
    if session_path.suffix == ".gz":
        with gzip.open(session_path, "rt", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(session_path, encoding="utf-8") as f:
            return json.load(f)


def replay_request(
    client: httpx.Client,
    request_data: dict[str, Any],
    timeout: float = 30.0,
) -> ReplayResult:
    """
    Replay a single recorded request.

    Args:
        client: HTTP client to use
        request_data: Recorded request data
        timeout: Request timeout in seconds

    Returns:
        ReplayResult with comparison
    """
    method = request_data["method"]
    path = request_data["path"]
    query = request_data.get("query_string", "")
    headers = request_data.get("headers", {})
    body = request_data.get("body")

    # Remove host header (will be set by client)
    headers.pop("host", None)
    headers.pop("content-length", None)

    # Build URL
    url = path
    if query:
        url = f"{path}?{query}"

    start_time = time.perf_counter()
    error = None
    actual_status = 0

    try:
        if body and method in ("POST", "PUT", "PATCH"):
            # Try to parse as JSON
            try:
                json_body = json.loads(body)
                response = client.request(
                    method=method,
                    url=url,
                    json=json_body,
                    headers=headers,
                    timeout=timeout,
                )
            except json.JSONDecodeError:
                response = client.request(
                    method=method,
                    url=url,
                    content=body.encode("utf-8"),
                    headers=headers,
                    timeout=timeout,
                )
        else:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
            )

        actual_status = response.status_code

    except Exception as e:
        error = str(e)
        actual_status = 0

    duration_ms = (time.perf_counter() - start_time) * 1000

    return ReplayResult(
        request_index=0,  # Set by caller
        method=method,
        path=path,
        expected_status=0,  # Set by caller
        actual_status=actual_status,
        status_match=False,  # Set by caller
        response_time_ms=duration_ms,
        error=error,
    )


def replay_session(
    session_path: Path,
    base_url: str = "http://localhost:8001",
    timeout: float = 30.0,
    stop_on_error: bool = False,
    verbose: bool = False,
) -> SessionReplayReport:
    """
    Replay an entire recorded session.

    Args:
        session_path: Path to session file
        base_url: Base URL of the backend
        timeout: Request timeout in seconds
        stop_on_error: Stop on first error
        verbose: Print detailed output

    Returns:
        SessionReplayReport with all results
    """
    session_data = load_session(session_path)
    session_id = session_data.get("session_id", "unknown")
    exchanges = session_data.get("exchanges", [])

    results: list[ReplayResult] = []
    successful = 0
    failed = 0
    status_mismatches = 0

    start_time = time.perf_counter()

    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        for i, exchange in enumerate(exchanges):
            request_data = exchange.get("request", {})
            response_data = exchange.get("response", {})
            expected_status = response_data.get("status_code", 200)

            if verbose:
                print(f"[{i+1}/{len(exchanges)}] {request_data['method']} {request_data['path']}")

            result = replay_request(client, request_data, timeout)
            result.request_index = i
            result.expected_status = expected_status
            result.status_match = result.actual_status == expected_status

            if result.error:
                failed += 1
                if verbose:
                    print(f"  ERROR: {result.error}")
            elif result.status_match:
                successful += 1
                if verbose:
                    print(f"  OK: {result.actual_status} ({result.response_time_ms:.1f}ms)")
            else:
                status_mismatches += 1
                if verbose:
                    print(f"  MISMATCH: expected {expected_status}, got {result.actual_status}")

            results.append(result)

            if stop_on_error and (result.error or not result.status_match):
                break

    total_time_ms = (time.perf_counter() - start_time) * 1000

    return SessionReplayReport(
        session_id=session_id,
        total_requests=len(exchanges),
        successful_replays=successful,
        failed_replays=failed,
        status_mismatches=status_mismatches,
        results=results,
        total_time_ms=total_time_ms,
    )


def main():
    """CLI entry point for request replayer."""
    parser = argparse.ArgumentParser(
        description="Replay recorded HTTP sessions for debugging and regression testing"
    )
    parser.add_argument(
        "session_file",
        type=Path,
        help="Path to session file (*.json or *.json.gz)",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8001",
        help="Base URL of the backend (default: http://localhost:8001)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop on first error or status mismatch",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed output",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save report to JSON file",
    )

    args = parser.parse_args()

    if not args.session_file.exists():
        print(f"Error: Session file not found: {args.session_file}", file=sys.stderr)
        sys.exit(1)

    print(f"Replaying session: {args.session_file}")
    print(f"Target: {args.base_url}")
    print()

    report = replay_session(
        session_path=args.session_file,
        base_url=args.base_url,
        timeout=args.timeout,
        stop_on_error=args.stop_on_error,
        verbose=args.verbose,
    )

    print()
    print("=" * 60)
    print("REPLAY SUMMARY")
    print("=" * 60)
    print(f"Session ID:       {report.session_id}")
    print(f"Total requests:   {report.total_requests}")
    print(f"Successful:       {report.successful_replays}")
    print(f"Failed:           {report.failed_replays}")
    print(f"Status mismatch:  {report.status_mismatches}")
    print(f"Total time:       {report.total_time_ms:.1f}ms")
    print()

    # Calculate pass rate
    if report.total_requests > 0:
        pass_rate = (report.successful_replays / report.total_requests) * 100
        print(f"Pass rate:        {pass_rate:.1f}%")

    # Save report if requested
    if args.output:
        report_data = {
            "session_id": report.session_id,
            "total_requests": report.total_requests,
            "successful_replays": report.successful_replays,
            "failed_replays": report.failed_replays,
            "status_mismatches": report.status_mismatches,
            "total_time_ms": report.total_time_ms,
            "results": [
                {
                    "index": r.request_index,
                    "method": r.method,
                    "path": r.path,
                    "expected_status": r.expected_status,
                    "actual_status": r.actual_status,
                    "status_match": r.status_match,
                    "response_time_ms": r.response_time_ms,
                    "error": r.error,
                }
                for r in report.results
            ],
        }

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        print(f"Report saved to: {args.output}")

    # Exit with error if any failures
    if report.failed_replays > 0 or report.status_mismatches > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
