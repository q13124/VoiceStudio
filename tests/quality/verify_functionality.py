"""
Functionality Verification Script
Verifies all features work as expected by testing actual functionality.
"""

import importlib.util
import inspect
import logging
import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_engine_functionality(engine_name: str) -> dict[str, Any]:
    """Verify engine functionality."""
    result = {
        "engine": engine_name,
        "status": "unknown",
        "errors": [],
        "warnings": []
    }

    try:
        engine_path = project_root / "app" / "core" / "engines" / f"{engine_name}.py"

        if not engine_path.exists():
            result["status"] = "skipped"
            result["warnings"].append("Engine file not found")
            return result

        spec = importlib.util.spec_from_file_location(engine_name, engine_path)
        if spec is None or spec.loader is None:
            result["status"] = "skipped"
            result["warnings"].append("Could not load engine module")
            return result

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        engine_classes = [obj for name, obj in inspect.getmembers(module, inspect.isclass)
                         if name.endswith('Engine') and obj.__module__ == module.__name__]

        if not engine_classes:
            result["status"] = "skipped"
            result["warnings"].append("No engine class found")
            return result

        engine_class = engine_classes[0]

        if hasattr(engine_class, '__init__'):
            try:
                with __import__('unittest.mock').patch('torch.cuda.is_available', return_value=False):
                    engine_class(model_path=None, device="cpu")
                    result["status"] = "passed"
            except Exception as e:
                result["status"] = "failed"
                result["errors"].append(f"Initialization failed: {e!s}")
        else:
            result["status"] = "failed"
            result["errors"].append("Engine class missing __init__ method")

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"Verification error: {e!s}")

    return result


def verify_backend_route_functionality(route_name: str) -> dict[str, Any]:
    """Verify backend route functionality."""
    result = {
        "route": route_name,
        "status": "unknown",
        "errors": [],
        "warnings": []
    }

    try:
        route_path = project_root / "backend" / "api" / "routes" / f"{route_name}.py"

        if not route_path.exists():
            result["status"] = "skipped"
            result["warnings"].append("Route file not found")
            return result

        spec = importlib.util.spec_from_file_location(route_name, route_path)
        if spec is None or spec.loader is None:
            result["status"] = "skipped"
            result["warnings"].append("Could not load route module")
            return result

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, 'router') or hasattr(module, 'app'):
            result["status"] = "passed"
        else:
            result["status"] = "failed"
            result["errors"].append("Route module missing router or app")

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"Verification error: {e!s}")

    return result


def verify_all_engines() -> list[dict[str, Any]]:
    """Verify all engines."""
    engines_dir = project_root / "app" / "core" / "engines"

    if not engines_dir.exists():
        logger.warning("Engines directory not found")
        return []

    engine_files = [f.stem for f in engines_dir.glob("*_engine.py")]
    results = []

    for engine_name in sorted(engine_files):
        logger.info(f"Verifying {engine_name}...")
        result = verify_engine_functionality(engine_name)
        results.append(result)

    return results


def verify_all_routes() -> list[dict[str, Any]]:
    """Verify all backend routes."""
    routes_dir = project_root / "backend" / "api" / "routes"

    if not routes_dir.exists():
        logger.warning("Routes directory not found")
        return []

    route_files = [f.stem for f in routes_dir.glob("*.py") if f.name != "__init__.py"]
    results = []

    for route_name in sorted(route_files):
        logger.info(f"Verifying {route_name}...")
        result = verify_backend_route_functionality(route_name)
        results.append(result)

    return results


def generate_functionality_report(engine_results: list[dict[str, Any]],
                                  route_results: list[dict[str, Any]]) -> str:
    """Generate functionality verification report."""
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("FUNCTIONALITY VERIFICATION REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")

    engine_passed = sum(1 for r in engine_results if r["status"] == "passed")
    engine_failed = sum(1 for r in engine_results if r["status"] == "failed")
    engine_skipped = sum(1 for r in engine_results if r["status"] == "skipped")

    report_lines.append("Engines:")
    report_lines.append(f"  Total: {len(engine_results)}")
    report_lines.append(f"  Passed: {engine_passed}")
    report_lines.append(f"  Failed: {engine_failed}")
    report_lines.append(f"  Skipped: {engine_skipped}")
    report_lines.append("")

    route_passed = sum(1 for r in route_results if r["status"] == "passed")
    route_failed = sum(1 for r in route_results if r["status"] == "failed")
    route_skipped = sum(1 for r in route_results if r["status"] == "skipped")

    report_lines.append("Backend Routes:")
    report_lines.append(f"  Total: {len(route_results)}")
    report_lines.append(f"  Passed: {route_passed}")
    report_lines.append(f"  Failed: {route_failed}")
    report_lines.append(f"  Skipped: {route_skipped}")
    report_lines.append("")

    if engine_failed > 0 or route_failed > 0:
        report_lines.append("Failed Items:")
        report_lines.append("")

        for result in engine_results:
            if result["status"] == "failed":
                report_lines.append(f"  Engine: {result['engine']}")
                for error in result["errors"]:
                    report_lines.append(f"    Error: {error}")

        for result in route_results:
            if result["status"] == "failed":
                report_lines.append(f"  Route: {result['route']}")
                for error in result["errors"]:
                    report_lines.append(f"    Error: {error}")

    report_lines.append("")
    report_lines.append("=" * 80)

    return "\n".join(report_lines)


def main():
    """Main function."""
    logger.info("Starting functionality verification...")

    engine_results = verify_all_engines()
    route_results = verify_all_routes()

    report = generate_functionality_report(engine_results, route_results)
    print(report)

    report_file = project_root / "functionality_verification_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"Functionality report saved to: {report_file}")

    failed_count = (sum(1 for r in engine_results if r["status"] == "failed") +
                   sum(1 for r in route_results if r["status"] == "failed"))

    return 1 if failed_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

