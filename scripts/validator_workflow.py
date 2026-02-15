#!/usr/bin/env python3
"""
Validator Workflow

Task-specific validation script that parses task briefs, extracts acceptance criteria,
runs verification commands, and generates validation checklists.

Usage:
  python scripts/validator_workflow.py --task TASK-0020
  python scripts/validator_workflow.py --task TASK-0020 --run-verification

Exit codes:
  0 - Validation passed (all criteria met)
  1 - Validation failed (one or more criteria not met)
  2 - Task brief not found or parse error

Per .cursor/rules/workflows/verifier-subagent.mdc and docs/governance/SKEPTICAL_VALIDATOR_GUIDE.md
"""

import argparse
import io
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def find_task_brief(task_id: str, project_root: Path) -> Path | None:
    """Find the task brief file for a given task ID."""
    # Normalize task ID format
    task_id_normalized = task_id.upper().replace("TASK-", "TASK-")
    if not task_id_normalized.startswith("TASK-"):
        task_id_normalized = f"TASK-{task_id_normalized}"

    # Check standard location
    task_file = project_root / "docs" / "tasks" / f"{task_id_normalized}.md"
    if task_file.exists():
        return task_file

    # Try lowercase
    task_file_lower = project_root / "docs" / "tasks" / f"{task_id_normalized.lower()}.md"
    if task_file_lower.exists():
        return task_file_lower

    return None


def parse_task_brief(task_file: Path) -> dict[str, Any]:
    """Parse a task brief and extract key sections."""
    content = task_file.read_text(encoding="utf-8")

    result = {
        "task_id": task_file.stem,
        "file_path": str(task_file),
        "title": "",
        "objective": "",
        "acceptance_criteria": [],
        "required_proofs": [],
        "affected_modules": [],
        "constraints": [],
        "status": "",
        "owner": "",
        "tech_debt": [],
    }

    # Extract title (first # heading)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Extract sections by heading
    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)

    for section in sections[1:]:  # Skip content before first ##
        lines = section.strip().split("\n")
        if not lines:
            continue

        heading = lines[0].strip().lower()
        body = "\n".join(lines[1:]).strip()

        if "objective" in heading:
            result["objective"] = body

        elif "acceptance criteria" in heading:
            # Extract checkbox items
            criteria = re.findall(r"^-\s*\[([ xX])\]\s*(.+)$", body, re.MULTILINE)
            result["acceptance_criteria"] = [
                {"text": text.strip(), "checked": check.lower() == "x"}
                for check, text in criteria
            ]

        elif "required proofs" in heading:
            proofs = re.findall(r"^-\s*\[([ xX])\]\s*(.+)$", body, re.MULTILINE)
            result["required_proofs"] = [
                {"text": text.strip(), "checked": check.lower() == "x"}
                for check, text in proofs
            ]

        elif "affected modules" in heading:
            modules = re.findall(r"^-\s*\[([ xX])\]\s*(.+)$", body, re.MULTILINE)
            result["affected_modules"] = [
                {"path": text.strip(), "checked": check.lower() == "x"}
                for check, text in modules
            ]

        elif "constraints" in heading:
            constraints = re.findall(r"^-\s+(.+)$", body, re.MULTILINE)
            result["constraints"] = [c.strip() for c in constraints]

        elif "status" in heading:
            # Find checked status
            status_match = re.search(r"-\s*\[x\]\s*(\w+)", body, re.IGNORECASE)
            if status_match:
                result["status"] = status_match.group(1).strip()

        elif "owner" in heading:
            result["owner"] = body.split("\n")[0].strip().lstrip("-").strip()

        elif "tech debt" in heading:
            debts = re.findall(r"\*\*(TD-\d+)\*\*", body)
            result["tech_debt"] = debts

    return result


def run_verification_checks(project_root: Path) -> dict[str, Any]:
    """Run the standard verification checks (gate status, ledger validate)."""
    result = subprocess.run(
        [sys.executable, "scripts/run_verification.py"],
        capture_output=True,
        text=True,
        cwd=project_root,
        timeout=60
    )

    # Try to read the JSON report
    report_file = project_root / ".buildlogs" / "verification" / "last_run.json"
    if report_file.exists():
        with open(report_file, encoding="utf-8") as f:
            return json.load(f)

    return {
        "all_passed": result.returncode == 0,
        "exit_code": result.returncode,
        "output": result.stdout + result.stderr
    }


def generate_validation_report(
    task_data: dict[str, Any],
    verification_result: dict[str, Any] | None,
    project_root: Path
) -> dict[str, Any]:
    """Generate a comprehensive validation report."""

    # Calculate completion status
    criteria_total = len(task_data["acceptance_criteria"])
    criteria_checked = sum(1 for c in task_data["acceptance_criteria"] if c["checked"])

    proofs_total = len(task_data["required_proofs"])
    proofs_checked = sum(1 for p in task_data["required_proofs"] if p["checked"])

    # Determine overall status
    criteria_complete = criteria_total > 0 and criteria_checked == criteria_total
    proofs_complete = proofs_total > 0 and proofs_checked == proofs_total
    verification_passed = verification_result.get("all_passed", True) if verification_result else True
    checks = verification_result.get("checks", []) if verification_result else []
    completion_guard_check = next((c for c in checks if c.get("name") == "completion_guard"), None)
    completion_guard_status = (
        "PASS" if completion_guard_check and completion_guard_check.get("passed") else
        "FAIL" if completion_guard_check else "SKIPPED"
    )

    all_passed = criteria_complete and proofs_complete and verification_passed

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": task_data["task_id"],
        "task_title": task_data["title"],
        "task_file": task_data["file_path"],
        "validation_result": "PASS" if all_passed else "FAIL",
        "summary": {
            "acceptance_criteria": f"{criteria_checked}/{criteria_total}",
            "required_proofs": f"{proofs_checked}/{proofs_total}",
            "verification": "PASS" if verification_passed else "FAIL" if verification_result else "SKIPPED",
            "completion_guard": completion_guard_status,
        },
        "acceptance_criteria": [
            {
                "criterion": c["text"],
                "status": "PASS" if c["checked"] else "PENDING"
            }
            for c in task_data["acceptance_criteria"]
        ],
        "required_proofs": [
            {
                "proof": p["text"],
                "status": "PRESENT" if p["checked"] else "MISSING"
            }
            for p in task_data["required_proofs"]
        ],
        "verification_checks": verification_result.get("checks", []) if verification_result else [],
        "diagnosis": [],
        "next_steps": []
    }

    # Add diagnosis for failures
    if not criteria_complete:
        pending = [c["text"] for c in task_data["acceptance_criteria"] if not c["checked"]]
        report["diagnosis"].append(f"Pending acceptance criteria: {len(pending)}")
        for p in pending[:5]:  # Show first 5
            report["diagnosis"].append(f"  - {p[:80]}...")

    if not proofs_complete:
        missing = [p["text"] for p in task_data["required_proofs"] if not p["checked"]]
        report["diagnosis"].append(f"Missing required proofs: {len(missing)}")
        for m in missing[:5]:
            report["diagnosis"].append(f"  - {m[:80]}...")

    if verification_result and not verification_passed:
        failed_checks = [c["name"] for c in verification_result.get("checks", []) if not c.get("passed")]
        report["diagnosis"].append(f"Failed verification checks: {failed_checks}")

    # Add next steps
    if not all_passed:
        report["next_steps"].append("Return to Construct phase to address failures")
        report["next_steps"].append("Do not close the task until all criteria are met")
        if task_data["owner"]:
            report["next_steps"].append(f"Owner: {task_data['owner']}")
    else:
        report["next_steps"].append("Task ready for closure per closure-protocol.mdc")
        report["next_steps"].append("Update task brief status to Complete")
        report["next_steps"].append("Update STATE.md with completion evidence")

    return report


def print_report(report: dict[str, Any]) -> None:
    """Print the validation report to console."""
    print()
    print("=" * 70)
    print("SKEPTICAL VALIDATOR REPORT")
    print("=" * 70)
    print()
    print(f"Task: {report['task_id']}")
    print(f"Title: {report['task_title']}")
    print(f"File: {report['task_file']}")
    print()

    # Overall result with visual indicator
    result = report["validation_result"]
    if result == "PASS":
        print("  RESULT: [PASS] - Task validation successful")
    else:
        print("  RESULT: [FAIL] - Task validation failed")
    print()

    # Summary
    print("Summary:")
    print(f"  Acceptance Criteria: {report['summary']['acceptance_criteria']}")
    print(f"  Required Proofs:     {report['summary']['required_proofs']}")
    print(f"  Verification Checks: {report['summary']['verification']}")
    print()

    # Acceptance criteria details
    if report["acceptance_criteria"]:
        print("Acceptance Criteria:")
        for c in report["acceptance_criteria"]:
            status = "[x]" if c["status"] == "PASS" else "[ ]"
            print(f"  {status} {c['criterion'][:70]}{'...' if len(c['criterion']) > 70 else ''}")
        print()

    # Required proofs details
    if report["required_proofs"]:
        print("Required Proofs:")
        for p in report["required_proofs"]:
            status = "[x]" if p["status"] == "PRESENT" else "[ ]"
            print(f"  {status} {p['proof'][:70]}{'...' if len(p['proof']) > 70 else ''}")
        print()

    # Verification checks
    if report["verification_checks"]:
        print("Verification Checks:")
        for check in report["verification_checks"]:
            status = "PASS" if check.get("passed") else "FAIL"
            print(f"  [{status}] {check.get('name', 'unknown')} (exit {check.get('exit_code', '?')})")
        print()

    # Diagnosis
    if report["diagnosis"]:
        print("Diagnosis:")
        for d in report["diagnosis"]:
            print(f"  {d}")
        print()

    # Next steps
    if report["next_steps"]:
        print("Next Steps:")
        for step in report["next_steps"]:
            print(f"  - {step}")
        print()

    print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate a task against its acceptance criteria and required proofs."
    )
    parser.add_argument(
        "--task", "-t",
        required=True,
        help="Task ID (e.g., TASK-0020 or 0020)"
    )
    parser.add_argument(
        "--run-verification", "-v",
        action="store_true",
        help="Also run verification checks (gate status, ledger validate)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output JSON report only (no console output)"
    )

    args = parser.parse_args()

    # Find project root
    project_root = Path(__file__).parent.parent

    # Find task brief
    task_file = find_task_brief(args.task, project_root)
    if not task_file:
        print(f"Error: Task brief not found for '{args.task}'", file=sys.stderr)
        print(f"  Expected: docs/tasks/TASK-{args.task.upper().replace('TASK-', '')}.md", file=sys.stderr)
        return 2

    # Parse task brief
    try:
        task_data = parse_task_brief(task_file)
    except Exception as e:
        print(f"Error parsing task brief: {e}", file=sys.stderr)
        return 2

    # Run verification if requested
    verification_result = None
    if args.run_verification:
        if not args.json:
            print("Running verification checks...")
        try:
            verification_result = run_verification_checks(project_root)
        except Exception as e:
            verification_result = {"all_passed": False, "error": str(e)}

    # Generate report
    report = generate_validation_report(task_data, verification_result, project_root)

    # Save JSON report
    output_dir = project_root / ".buildlogs" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = output_dir / f"{task_data['task_id']}_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Also save as latest for this task
    latest_file = output_dir / f"{task_data['task_id']}_latest.json"
    with open(latest_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Output
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
        print(f"  Report saved: {output_file}")
        print()

    # Return exit code based on result
    return 0 if report["validation_result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
