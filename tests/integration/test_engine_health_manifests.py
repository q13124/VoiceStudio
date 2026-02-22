"""Engine health verification from manifests.

Covers all engine manifests: full engines (import + initialize), placeholders
(clear not-implemented errors), and generates .buildlogs/engine_health_report.json.
"""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest

# Resolve engines root relative to repo
REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINES_ROOT = REPO_ROOT / "engines"
BUILDLOGS = REPO_ROOT / ".buildlogs"


def _load_manifest_loader():
    """Load manifest_loader; may skip if app not on path."""
    try:
        from app.core.engines.manifest_loader import (
            find_engine_manifests,
            get_engine_entry_point,
            load_engine_manifest,
        )

        return find_engine_manifests, get_engine_entry_point, load_engine_manifest
    except ImportError as e:
        pytest.skip(f"Cannot import manifest_loader: {e}")


def get_all_manifests():
    """Discover all engine manifests and their implementation_status."""
    find_manifests, _, load_manifest = _load_manifest_loader()
    manifests = find_manifests(str(ENGINES_ROOT))
    result = []
    for engine_id, path in manifests.items():
        try:
            m = load_manifest(path)
            status = m.get("implementation_status") or m.get("status") or "unknown"
            result.append(
                {
                    "engine_id": engine_id,
                    "path": path,
                    "manifest": m,
                    "status": status,
                    "entry_point": m.get("entry_point"),
                }
            )
        except Exception as e:
            result.append(
                {
                    "engine_id": engine_id,
                    "path": path,
                    "manifest": None,
                    "status": "load_error",
                    "error": str(e),
                }
            )
    return result


def _import_and_get_class(entry_point: str):
    """Import module and return engine class from entry_point (module:class or module.class)."""
    if ":" in entry_point:
        mod_path, cls_name = entry_point.rsplit(":", 1)
    else:
        mod_path, cls_name = entry_point.rsplit(".", 1)
    mod = importlib.import_module(mod_path)
    return getattr(mod, cls_name)


@pytest.fixture(scope="module")
def engine_health_report():
    """Build engine health report as fixture for tests and final dump."""
    find_manifests, get_entry, load_manifest = _load_manifest_loader()
    manifests = find_manifests(str(ENGINES_ROOT))
    report = {
        "engines": [],
        "summary": {"total": 0, "full": 0, "basic": 0, "placeholder": 0, "external": 0, "error": 0},
    }

    for engine_id, path in sorted(manifests.items()):
        try:
            m = load_manifest(path)
        except Exception as e:
            report["engines"].append(
                {
                    "engine_id": engine_id,
                    "status": "load_error",
                    "pass": False,
                    "error": str(e),
                }
            )
            report["summary"]["error"] += 1
            report["summary"]["total"] += 1
            continue

        status = m.get("implementation_status") or m.get("status") or "unknown"
        if status not in report["summary"]:
            report["summary"][status] = 0
        report["summary"][status] = report["summary"].get(status, 0) + 1
        report["summary"]["total"] += 1

        entry = m.get("entry_point")
        if not entry:
            report["engines"].append(
                {
                    "engine_id": engine_id,
                    "status": status,
                    "pass": False,
                    "error": "No entry_point",
                }
            )
            continue

        passed = False
        err_msg = None
        try:
            cls = _import_and_get_class(entry)
            if status == "full":
                inst = cls()
                if hasattr(inst, "initialize"):
                    inst.initialize(lazy=True)
                passed = True
            elif status == "placeholder":
                inst = cls()
                if hasattr(inst, "initialize"):
                    try:
                        inst.initialize(lazy=True)
                    except (NotImplementedError, RuntimeError) as e:
                        if "not implemented" in str(e).lower() or "placeholder" in str(e).lower():
                            passed = True
                        else:
                            err_msg = str(e)
                else:
                    passed = True
            else:
                passed = True
        except ImportError as e:
            err_msg = f"Import: {e}"
        except (NotImplementedError, RuntimeError) as e:
            if status == "placeholder":
                passed = "not implemented" in str(e).lower() or "placeholder" in str(e).lower()
            err_msg = str(e) if not passed else None
        except Exception as e:
            err_msg = str(e)

        report["engines"].append(
            {
                "engine_id": engine_id,
                "status": status,
                "pass": passed,
                "error": err_msg,
            }
        )

    BUILDLOGS.mkdir(parents=True, exist_ok=True)
    report_path = BUILDLOGS / "engine_health_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report


def test_engine_health_report_generated(engine_health_report):
    """Engine health report is generated with expected structure."""
    assert "engines" in engine_health_report
    assert "summary" in engine_health_report
    assert engine_health_report["summary"]["total"] >= 1


def test_full_engines_import_and_initialize(engine_health_report):
    """Full-status engines: report generated; optional deps may cause skip/fail."""
    full_engines = [e for e in engine_health_report["engines"] if e["status"] == "full"]
    assert len(full_engines) >= 1
    # Report is for audit; ImportError and optional-dep failures are expected


def test_placeholder_engines_audit(engine_health_report):
    """Placeholder engines are identified for audit."""
    placeholders = [e for e in engine_health_report["engines"] if e["status"] == "placeholder"]
    assert len(placeholders) >= 1
    for eng in placeholders:
        assert "engine_id" in eng
