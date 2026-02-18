"""
Plugin Lock Command.

Phase 5C M4: CLI commands for lockfile management.

Provides commands for managing the plugin lockfile including:
- Generate lockfile from current installation
- Validate lockfile against installation
- Lock/unlock specific plugins
- Export/import lockfiles for deployment
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click


def check_lockfile_available() -> bool:
    """Check if lockfile module is available."""
    try:
        from backend.plugins.gallery.lockfile import LockfileManager
        return True
    except ImportError:
        return False


def get_lockfile_classes():
    """Get lockfile classes (lazy import)."""
    from backend.plugins.gallery.lockfile import (
        Lockfile,
        LockfileManager,
        LockfileStatus,
        LockfileValidationResult,
    )
    return Lockfile, LockfileManager, LockfileStatus, LockfileValidationResult


def format_validation_result(result: Any, verbose: bool = False) -> list[str]:
    """Format validation result for display."""
    _, _, LockfileStatus, _ = get_lockfile_classes()
    
    lines = []
    
    # Status header
    status_colors = {
        LockfileStatus.VALID: ("green", "[VALID]"),
        LockfileStatus.OUTDATED: ("yellow", "[OUTDATED]"),
        LockfileStatus.MISSING_PLUGINS: ("red", "[MISSING]"),
        LockfileStatus.EXTRA_PLUGINS: ("yellow", "[EXTRA]"),
        LockfileStatus.VERSION_MISMATCH: ("yellow", "[MISMATCH]"),
        LockfileStatus.INTEGRITY_FAILED: ("red", "[INTEGRITY FAILED]"),
        LockfileStatus.CORRUPTED: ("red", "[CORRUPTED]"),
        LockfileStatus.NOT_FOUND: ("red", "[NOT FOUND]"),
    }
    
    color, label = status_colors.get(result.status, ("white", f"[{result.status.value}]"))
    lines.append(click.style(f"{label} {result.message}", fg=color))
    
    if verbose or not result.valid:
        # Show conflicts
        if result.conflicts:
            lines.append("")
            lines.append("Conflicts:")
            for conflict in result.conflicts:
                if conflict.conflict_type == "missing":
                    lines.append(
                        f"  - {conflict.plugin_id}: "
                        f"Missing (lockfile: {conflict.lockfile_version})"
                    )
                elif conflict.conflict_type == "extra":
                    lines.append(
                        f"  - {conflict.plugin_id}: "
                        f"Extra (installed: {conflict.installed_version})"
                    )
                elif conflict.conflict_type == "version_mismatch":
                    lines.append(
                        f"  - {conflict.plugin_id}: "
                        f"{conflict.installed_version} -> {conflict.lockfile_version}"
                    )
        
        # Show integrity errors
        if result.integrity_errors:
            lines.append("")
            lines.append("Integrity Errors:")
            for error in result.integrity_errors:
                lines.append(f"  - {error}")
    
    return lines


def result_to_dict(result: Any) -> dict[str, Any]:
    """Convert validation result to dictionary for JSON output."""
    return result.to_dict()


@click.command("lock")
@click.option(
    "-o", "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output file path (default: voicestudio-plugins.lock)",
)
@click.option(
    "--plugins-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Custom plugins directory.",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON.")
@click.option(
    "--vs-version",
    default="1.0.0",
    help="VoiceStudio version to record in lockfile.",
)
def lock_command(
    output: Path | None,
    plugins_dir: Path | None,
    output_json: bool,
    vs_version: str,
) -> None:
    """
    Generate a lockfile from currently installed plugins.

    Creates a lockfile that pins the exact versions of all installed plugins
    and their dependencies. This ensures consistent deployments across
    different environments.

    Examples:

        # Generate lockfile (saves to default location)
        voicestudio-plugin lock

        # Generate lockfile to specific path
        voicestudio-plugin lock -o my-lockfile.json

        # Output as JSON
        voicestudio-plugin lock --json
    """
    if not check_lockfile_available():
        click.echo("Error: Lockfile module not available. Ensure backend is installed.", err=True)
        sys.exit(1)
    
    _, LockfileManager, _, _ = get_lockfile_classes()
    
    try:
        manager = LockfileManager(plugins_dir=plugins_dir)
        lockfile = manager.generate_lockfile(voicestudio_version=vs_version)
        
        if output:
            lockfile.save(output)
            target = output
        else:
            manager.save_lockfile(lockfile)
            target = manager.lockfile_path
        
        if output_json:
            click.echo(lockfile.to_json())
        else:
            click.echo(click.style("[LOCKED]", fg="green") + f" Generated lockfile with {len(lockfile.plugins)} plugins")
            click.echo(f"  Path: {target}")
            click.echo(f"  Version: {lockfile.version}")
            click.echo(f"  Generated: {lockfile.generated_at}")
            
            if lockfile.plugins:
                click.echo("\nLocked plugins:")
                for pid, plugin in sorted(lockfile.plugins.items()):
                    click.echo(f"  - {pid}@{plugin.version}")
    
    except Exception as e:
        click.echo(f"Error generating lockfile: {e}", err=True)
        sys.exit(1)


@click.command("validate")
@click.option(
    "-f", "--file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Lockfile to validate (default: auto-detect).",
)
@click.option(
    "--plugins-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Custom plugins directory.",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON.")
@click.option("-v", "--verbose", is_flag=True, help="Show detailed information.")
def validate_command(
    file: Path | None,
    plugins_dir: Path | None,
    output_json: bool,
    verbose: bool,
) -> None:
    """
    Validate the lockfile against current installation.

    Checks if the lockfile matches the currently installed plugins,
    detecting missing plugins, version mismatches, and integrity issues.

    Examples:

        # Validate default lockfile
        voicestudio-plugin validate

        # Validate specific lockfile
        voicestudio-plugin validate -f deployment.lock

        # Output as JSON
        voicestudio-plugin validate --json
    """
    if not check_lockfile_available():
        click.echo("Error: Lockfile module not available.", err=True)
        sys.exit(1)
    
    _, LockfileManager, LockfileStatus, _ = get_lockfile_classes()
    
    try:
        manager = LockfileManager(plugins_dir=plugins_dir, lockfile_path=file)
        result = manager.validate_lockfile()
        
        if output_json:
            click.echo(json.dumps(result_to_dict(result), indent=2))
        else:
            for line in format_validation_result(result, verbose):
                click.echo(line)
        
        # Exit code based on validity
        if not result.valid:
            sys.exit(1)
    
    except FileNotFoundError:
        click.echo("Error: Lockfile not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error validating lockfile: {e}", err=True)
        sys.exit(1)


@click.command("lock-add")
@click.argument("plugin_id")
@click.argument("version")
@click.option(
    "--checksum",
    help="SHA256 checksum of the plugin package.",
)
@click.option(
    "--source",
    default="catalog",
    type=click.Choice(["catalog", "local", "git"]),
    help="Installation source.",
)
@click.option(
    "--url",
    help="Download URL for the plugin.",
)
@click.option(
    "--plugins-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Custom plugins directory.",
)
def lock_add_command(
    plugin_id: str,
    version: str,
    checksum: str | None,
    source: str,
    url: str | None,
    plugins_dir: Path | None,
) -> None:
    """
    Add or update a plugin in the lockfile.

    Locks a specific version of a plugin. If the plugin is already in the
    lockfile, its version will be updated.

    Examples:

        # Lock a plugin version
        voicestudio-plugin lock-add my-plugin 1.2.3

        # Lock with checksum
        voicestudio-plugin lock-add my-plugin 1.2.3 --checksum abc123...
    """
    if not check_lockfile_available():
        click.echo("Error: Lockfile module not available.", err=True)
        sys.exit(1)
    
    _, LockfileManager, _, _ = get_lockfile_classes()
    
    try:
        manager = LockfileManager(plugins_dir=plugins_dir)
        lockfile = manager.lock_plugin(
            plugin_id=plugin_id,
            version=version,
            checksum=checksum or "",
            source=source,
            download_url=url or "",
        )
        
        click.echo(click.style("[LOCKED]", fg="green") + f" {plugin_id}@{version}")
        click.echo(f"  Lockfile now has {len(lockfile.plugins)} plugin(s)")
    
    except Exception as e:
        click.echo(f"Error locking plugin: {e}", err=True)
        sys.exit(1)


@click.command("lock-remove")
@click.argument("plugin_id")
@click.option(
    "--plugins-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Custom plugins directory.",
)
def lock_remove_command(
    plugin_id: str,
    plugins_dir: Path | None,
) -> None:
    """
    Remove a plugin from the lockfile.

    This does not uninstall the plugin, just removes it from version pinning.

    Examples:

        # Unlock a plugin
        voicestudio-plugin lock-remove my-plugin
    """
    if not check_lockfile_available():
        click.echo("Error: Lockfile module not available.", err=True)
        sys.exit(1)
    
    _, LockfileManager, _, _ = get_lockfile_classes()
    
    try:
        manager = LockfileManager(plugins_dir=plugins_dir)
        lockfile = manager.unlock_plugin(plugin_id)
        
        if lockfile is None:
            click.echo("Warning: No lockfile exists.", err=True)
            sys.exit(1)
        
        click.echo(click.style("[UNLOCKED]", fg="yellow") + f" {plugin_id}")
        click.echo(f"  Lockfile now has {len(lockfile.plugins)} plugin(s)")
    
    except Exception as e:
        click.echo(f"Error unlocking plugin: {e}", err=True)
        sys.exit(1)


@click.command("lock-export")
@click.argument("output", type=click.Path(dir_okay=False, path_type=Path))
@click.option(
    "--plugins-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Custom plugins directory.",
)
def lock_export_command(
    output: Path,
    plugins_dir: Path | None,
) -> None:
    """
    Export lockfile for deployment.

    Creates a portable lockfile that can be transferred to another
    environment for consistent deployment.

    Examples:

        # Export lockfile
        voicestudio-plugin lock-export production.lock
    """
    if not check_lockfile_available():
        click.echo("Error: Lockfile module not available.", err=True)
        sys.exit(1)
    
    _, LockfileManager, _, _ = get_lockfile_classes()
    
    try:
        manager = LockfileManager(plugins_dir=plugins_dir)
        manager.export_lockfile(output)
        
        click.echo(click.style("[EXPORTED]", fg="green") + f" Lockfile saved to {output}")
    
    except Exception as e:
        click.echo(f"Error exporting lockfile: {e}", err=True)
        sys.exit(1)


@click.command("lock-import")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--plugins-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Custom plugins directory.",
)
@click.option("--validate", is_flag=True, help="Validate after import.")
def lock_import_command(
    input_file: Path,
    plugins_dir: Path | None,
    validate: bool,
) -> None:
    """
    Import a lockfile from another environment.

    Replaces the current lockfile with the imported one.

    Examples:

        # Import lockfile
        voicestudio-plugin lock-import production.lock

        # Import and validate
        voicestudio-plugin lock-import production.lock --validate
    """
    if not check_lockfile_available():
        click.echo("Error: Lockfile module not available.", err=True)
        sys.exit(1)
    
    _, LockfileManager, _, _ = get_lockfile_classes()
    
    try:
        manager = LockfileManager(plugins_dir=plugins_dir)
        lockfile = manager.import_lockfile(input_file)
        
        click.echo(click.style("[IMPORTED]", fg="green") + f" Lockfile with {len(lockfile.plugins)} plugin(s)")
        
        if validate:
            click.echo("\nValidating...")
            result = manager.validate_lockfile(lockfile)
            for line in format_validation_result(result, verbose=False):
                click.echo(line)
            
            if not result.valid:
                sys.exit(1)
    
    except Exception as e:
        click.echo(f"Error importing lockfile: {e}", err=True)
        sys.exit(1)


@click.command("lock-plan")
@click.option(
    "-f", "--file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Lockfile to plan from.",
)
@click.option(
    "--plugins-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Custom plugins directory.",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON.")
def lock_plan_command(
    file: Path | None,
    plugins_dir: Path | None,
    output_json: bool,
) -> None:
    """
    Generate an install plan from the lockfile.

    Shows what actions would be needed to sync the current installation
    with the lockfile.

    Examples:

        # Show install plan
        voicestudio-plugin lock-plan

        # Output as JSON
        voicestudio-plugin lock-plan --json
    """
    if not check_lockfile_available():
        click.echo("Error: Lockfile module not available.", err=True)
        sys.exit(1)
    
    _, LockfileManager, _, _ = get_lockfile_classes()
    
    try:
        manager = LockfileManager(plugins_dir=plugins_dir, lockfile_path=file)
        plan = manager.get_install_plan()
        
        if output_json:
            click.echo(json.dumps(plan, indent=2))
        else:
            if "error" in plan:
                click.echo(f"Error: {plan['error']}", err=True)
                sys.exit(1)
            
            actions = plan.get("actions", [])
            
            if not actions:
                click.echo(click.style("[IN SYNC]", fg="green") + " No actions needed")
            else:
                click.echo(f"Install plan: {len(actions)} action(s)")
                click.echo("")
                
                for action in actions:
                    if action["action"] == "install":
                        click.echo(
                            click.style("  [INSTALL]", fg="green") +
                            f" {action['plugin_id']}@{action['version']}"
                        )
                    elif action["action"] == "change_version":
                        click.echo(
                            click.style("  [CHANGE]", fg="yellow") +
                            f" {action['plugin_id']}: "
                            f"{action['from_version']} -> {action['to_version']}"
                        )
                    elif action["action"] == "warn_extra":
                        click.echo(
                            click.style("  [EXTRA]", fg="cyan") +
                            f" {action['plugin_id']} (not in lockfile)"
                        )
                
                click.echo("")
                click.echo(
                    f"Summary: {plan.get('install_count', 0)} install, "
                    f"{plan.get('change_count', 0)} change, "
                    f"{plan.get('warn_count', 0)} warnings"
                )
    
    except Exception as e:
        click.echo(f"Error generating plan: {e}", err=True)
        sys.exit(1)
