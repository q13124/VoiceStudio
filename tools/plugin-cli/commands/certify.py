"""
Plugin Certify Command.

Automated quality gate certification for VoiceStudio plugins.

Phase 5C M3: Creates certification engine CLI command that runs automated
quality gates including manifest validation, vulnerability scanning, SBOM
validation, license compliance, signature verification, and build provenance.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click


def check_certification_available() -> bool:
    """Check if certification engine dependencies are available."""
    try:
        from backend.plugins.supply_chain.certification import CertificationEngine
        return True
    except ImportError:
        return False


def get_certification_engine():
    """Get the certification engine (lazy import to avoid load time)."""
    from backend.plugins.supply_chain.certification import (
        CertificationEngine,
        CertificationLevel,
        CertificationPolicy,
    )
    return CertificationEngine, CertificationLevel, CertificationPolicy


def format_gate_result(gate: Any, verbose: bool = False) -> str:
    """Format a single gate result for display."""
    from backend.plugins.supply_chain.certification import GateStatus

    # Status icons
    icons = {
        GateStatus.PASSED: click.style("[PASS]", fg="green"),
        GateStatus.FAILED: click.style("[FAIL]", fg="red"),
        GateStatus.SKIPPED: click.style("[SKIP]", fg="yellow"),
        GateStatus.NOT_APPLICABLE: click.style("[N/A]", fg="cyan"),
    }

    icon = icons.get(gate.status, "[?]")
    line = f"  {icon} {gate.name}"

    if gate.status == GateStatus.FAILED and gate.message:
        line += f"\n        Reason: {gate.message}"
    elif verbose and gate.message:
        line += f" - {gate.message}"

    return line


def format_certification_result(result: Any, verbose: bool = False) -> List[str]:
    """Format certification result for display."""
    from backend.plugins.supply_chain.certification import CertificationLevel, GateStatus

    lines = []

    # Header
    if result.certified:
        level_colors = {
            CertificationLevel.BASIC: "green",
            CertificationLevel.STANDARD: "cyan",
            CertificationLevel.PREMIUM: "blue",
            CertificationLevel.ENTERPRISE: "magenta",
        }
        color = level_colors.get(result.level, "white")
        lines.append(
            click.style(
                f"[CERTIFIED] {result.level.value.upper()}",
                fg=color,
                bold=True
            )
        )
    else:
        lines.append(click.style("[NOT CERTIFIED]", fg="red", bold=True))

    lines.append("")

    # Plugin info
    lines.append(f"Plugin: {result.plugin_id} v{result.version}")
    lines.append(f"Certificate ID: {result.certificate_id}")
    lines.append(f"Certified at: {result.certified_at}")

    if result.expires_at:
        lines.append(f"Expires: {result.expires_at}")

    lines.append("")

    # Quality gates
    lines.append("Quality Gates:")

    # Group by status for cleaner display
    passed = [g for g in result.quality_gates if g.status == GateStatus.PASSED]
    failed = [g for g in result.quality_gates if g.status == GateStatus.FAILED]
    skipped = [g for g in result.quality_gates if g.status == GateStatus.SKIPPED]
    errors = [g for g in result.quality_gates if g.status == GateStatus.ERROR]

    for gate in passed:
        lines.append(format_gate_result(gate, verbose))
    for gate in failed:
        lines.append(format_gate_result(gate, verbose))
    for gate in skipped:
        lines.append(format_gate_result(gate, verbose))
    for gate in errors:
        lines.append(format_gate_result(gate, verbose))

    # Summary
    lines.append("")
    total = len(result.quality_gates)
    passed_count = len(passed)
    failed_count = len(failed)
    lines.append(
        f"Summary: {passed_count}/{total} gates passed"
        + (f", {failed_count} failed" if failed_count > 0 else "")
    )

    # Metrics (if verbose)
    if verbose and result.metrics:
        lines.append("")
        lines.append("Metrics:")
        if result.metrics.vulnerability_count is not None:
            lines.append(f"  Vulnerabilities: {result.metrics.vulnerability_count}")
        if result.metrics.dependency_count is not None:
            lines.append(f"  Dependencies: {result.metrics.dependency_count}")
        if result.metrics.test_coverage is not None:
            lines.append(f"  Test coverage: {result.metrics.test_coverage}%")
        if result.metrics.code_size_kb is not None:
            lines.append(f"  Code size: {result.metrics.code_size_kb} KB")

    return lines


def result_to_dict(result: Any) -> Dict[str, Any]:
    """Convert certification result to JSON-serializable dict."""
    from backend.plugins.supply_chain.certification import CertificationLevel, GateStatus

    def enum_to_str(val):
        return val.value if hasattr(val, "value") else str(val)

    gates = []
    for gate in result.quality_gates:
        gates.append({
            "id": gate.gate_id,
            "name": gate.name,
            "status": enum_to_str(gate.status),
            "message": gate.message,
            "checked_at": gate.checked_at,
        })

    metrics = None
    if result.metrics:
        metrics = {
            "vulnerability_count": result.metrics.vulnerability_count,
            "dependency_count": result.metrics.dependency_count,
            "test_coverage": result.metrics.test_coverage,
            "code_size_kb": result.metrics.code_size_kb,
            "lines_of_code": result.metrics.lines_of_code,
        }

    return {
        "certified": result.certified,
        "level": enum_to_str(result.level),
        "plugin_id": result.plugin_id,
        "version": result.version,
        "certificate_id": result.certificate_id,
        "certified_at": result.certified_at,
        "expires_at": result.expires_at,
        "certifier": result.certifier,
        "quality_gates": gates,
        "metrics": metrics,
    }


@click.command("certify")
@click.argument(
    "package",
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "-l", "--level",
    type=click.Choice(["basic", "standard", "premium", "enterprise"]),
    default="standard",
    help="Target certification level (default: standard).",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Fail on any gate failure (even optional ones).",
)
@click.option(
    "--keystore",
    type=click.Path(exists=True),
    help="Keystore directory for signature verification.",
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Write certification result to file.",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON.",
)
@click.option(
    "--update-manifest",
    is_flag=True,
    help="Update package manifest with certification metadata.",
)
@click.pass_context
def certify_command(
    ctx: click.Context,
    package: str,
    level: str,
    strict: bool,
    keystore: Optional[str],
    output: Optional[str],
    output_json: bool,
    update_manifest: bool,
) -> None:
    """
    Run automated certification for a plugin package.

    Executes quality gates including:
    - Manifest validation
    - Vulnerability scanning
    - SBOM validation
    - License compatibility
    - Signature verification (premium+)
    - Build provenance (premium+)

    The certification level determines which gates must pass:

    \b
    - BASIC: Manifest + no critical vulnerabilities
    - STANDARD: Basic + SBOM + license compliance
    - PREMIUM: Standard + signature + provenance
    - ENTERPRISE: Premium + tests + performance + security review

    Examples:

    \b
        # Run standard certification
        voicestudio-plugin certify my-plugin-1.0.0.vspkg

        # Target enterprise level
        voicestudio-plugin certify my-plugin-1.0.0.vspkg --level enterprise

        # Output results as JSON
        voicestudio-plugin certify my-plugin-1.0.0.vspkg --json

        # Save certification result to file
        voicestudio-plugin certify my-plugin-1.0.0.vspkg -o cert-result.json
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)

    # Check dependencies
    if not check_certification_available():
        raise click.ClickException(
            "Certification engine not available. "
            "Ensure backend.plugins.supply_chain is installed."
        )

    package_path = Path(package).resolve()

    if not quiet and not output_json:
        click.echo(f"Certifying: {package_path.name}")
        click.echo(f"Target level: {level}")
        click.echo("")

    # Import and configure engine
    CertificationEngine, CertificationLevel, CertificationPolicy = get_certification_engine()

    # Map level string to enum
    level_map = {
        "basic": CertificationLevel.BASIC,
        "standard": CertificationLevel.STANDARD,
        "premium": CertificationLevel.PREMIUM,
        "enterprise": CertificationLevel.ENTERPRISE,
    }
    target_level = level_map[level]

    # Build policy
    policy = CertificationPolicy(
        target_level=target_level,
        strict_mode=strict,
    )

    # Create engine
    keystore_path = Path(keystore) if keystore else None
    engine = CertificationEngine(
        keystore_path=keystore_path,
        policy=policy,
    )

    # Run certification
    try:
        result = asyncio.run(engine.certify_package(package_path))
    except Exception as e:
        if output_json:
            click.echo(json.dumps({
                "error": True,
                "message": str(e),
                "package": str(package_path),
            }))
        else:
            raise click.ClickException(f"Certification failed: {e}")
        raise SystemExit(1)

    # Output results
    if output_json:
        click.echo(json.dumps(result_to_dict(result), indent=2))
    else:
        if not quiet:
            for line in format_certification_result(result, verbose):
                click.echo(line)

    # Write to output file if requested
    if output:
        output_path = Path(output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_to_dict(result), f, indent=2)
        if not quiet and not output_json:
            click.echo("")
            click.echo(f"Result written to: {output_path}")

    # Exit code based on certification status
    if not result.certified:
        if not quiet and not output_json:
            click.echo("")
            click.echo(
                click.style(
                    f"Certification failed for {level.upper()} level.",
                    fg="red"
                )
            )
            click.echo("Review failed gates above and address issues.")
        raise SystemExit(1)

    if not quiet and not output_json:
        click.echo("")
        click.echo(click.style("Certification successful!", fg="green", bold=True))


@click.command("cert-info")
@click.argument(
    "result_file",
    type=click.Path(exists=True),
    required=True,
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON.",
)
@click.pass_context
def cert_info_command(
    ctx: click.Context,
    result_file: str,
    output_json: bool,
) -> None:
    """
    Display information from a certification result file.

    Reads a JSON certification result file and displays formatted information
    about the certification status, quality gates, and metrics.

    Examples:

    \b
        voicestudio-plugin cert-info cert-result.json
    """
    result_path = Path(result_file).resolve()

    with open(result_path, encoding="utf-8") as f:
        data = json.load(f)

    if output_json:
        click.echo(json.dumps(data, indent=2))
        return

    # Display formatted info
    click.echo("=" * 60)
    click.echo("CERTIFICATION RESULT")
    click.echo("=" * 60)
    click.echo("")

    if data.get("certified"):
        level = data.get("level", "unknown")
        click.echo(click.style(f"Status: CERTIFIED ({level.upper()})", fg="green", bold=True))
    else:
        click.echo(click.style("Status: NOT CERTIFIED", fg="red", bold=True))

    click.echo(f"Plugin: {data.get('plugin_id')} v{data.get('version')}")
    click.echo(f"Certificate ID: {data.get('certificate_id')}")
    click.echo(f"Certified at: {data.get('certified_at')}")

    if data.get("expires_at"):
        click.echo(f"Expires: {data.get('expires_at')}")

    click.echo("")
    click.echo("Quality Gates:")

    for gate in data.get("quality_gates", []):
        status = gate.get("status", "unknown")
        name = gate.get("name", gate.get("id", "unknown"))

        if status == "passed":
            icon = click.style("[PASS]", fg="green")
        elif status == "failed":
            icon = click.style("[FAIL]", fg="red")
        elif status == "skipped":
            icon = click.style("[SKIP]", fg="yellow")
        else:
            icon = click.style("[ERR]", fg="magenta")

        click.echo(f"  {icon} {name}")
        if status == "failed" and gate.get("message"):
            click.echo(f"        Reason: {gate.get('message')}")

    metrics = data.get("metrics")
    if metrics:
        click.echo("")
        click.echo("Metrics:")
        if metrics.get("vulnerability_count") is not None:
            click.echo(f"  Vulnerabilities: {metrics.get('vulnerability_count')}")
        if metrics.get("dependency_count") is not None:
            click.echo(f"  Dependencies: {metrics.get('dependency_count')}")
        if metrics.get("test_coverage") is not None:
            click.echo(f"  Test coverage: {metrics.get('test_coverage')}%")
