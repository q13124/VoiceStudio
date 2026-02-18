"""
Plugin Publish Command.

Publishes plugins to the VoiceStudio catalog.
"""

import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import click

# Default catalog URL
DEFAULT_CATALOG_URL = "https://catalog.voicestudio.ai/api/v1"


def load_package_manifest(package_path: Path) -> Dict[str, Any]:
    """Load the manifest from a .vspkg package."""
    with zipfile.ZipFile(package_path, "r") as zf:
        # Try package manifest first
        try:
            manifest_data = zf.read("VSPKG-MANIFEST.json")
            return json.loads(manifest_data)
        except KeyError:
            # SAFETY: Cascading fallback - try next manifest format
            pass
        
        # Try plugin manifest
        try:
            manifest_data = zf.read("plugin.json")
            return {"plugin": json.loads(manifest_data)}
        except KeyError:
            # SAFETY: Cascading fallback - try next manifest format
            pass
        
        # Try manifest.json
        try:
            manifest_data = zf.read("manifest.json")
            return {"plugin": json.loads(manifest_data)}
        except KeyError:
            # SAFETY: All manifest formats exhausted - fall through to raise
            pass
    
    raise click.ClickException(
        "Invalid package: No manifest found in .vspkg file"
    )


def load_signature(package_path: Path) -> Optional[Dict[str, Any]]:
    """Load the signature file for a package."""
    sig_path = package_path.with_suffix(package_path.suffix + ".sig")
    
    if not sig_path.exists():
        return None
    
    with open(sig_path, encoding="utf-8") as f:
        return json.load(f)


def validate_package_for_publish(
    package_path: Path,
    require_signature: bool = True,
) -> Dict[str, Any]:
    """
    Validate that a package is ready for publishing.
    
    Returns:
        Package metadata if valid
    """
    errors = []
    warnings = []
    
    # Check package exists
    if not package_path.exists():
        raise click.ClickException(f"Package not found: {package_path}")
    
    # Check it's a valid zip/vspkg
    if not zipfile.is_zipfile(package_path):
        raise click.ClickException("Invalid package: Not a valid .vspkg file")
    
    # Load manifest
    try:
        manifest = load_package_manifest(package_path)
    except Exception as e:
        raise click.ClickException(f"Failed to read package manifest: {e}")
    
    plugin_info = manifest.get("plugin", manifest)
    
    # Check required fields
    required = ["id", "name", "version"]
    for field in required:
        if field not in plugin_info or not plugin_info[field]:
            errors.append(f"Missing required field in manifest: {field}")
    
    # Check signature
    signature = load_signature(package_path)
    if require_signature and not signature:
        errors.append(
            "Package must be signed before publishing. "
            "Run: voicestudio-plugin sign <package>"
        )
    elif signature:
        # Verify signature matches package
        from .sign import verify_signature
        
        sig_path = package_path.with_suffix(package_path.suffix + ".sig")
        is_valid, message = verify_signature(package_path, sig_path)
        
        if not is_valid:
            errors.append(f"Invalid signature: {message}")
    
    # Check description
    if not plugin_info.get("description"):
        warnings.append("No description provided")
    
    # Check author
    author = plugin_info.get("author", {})
    if isinstance(author, dict):
        if not author.get("email"):
            warnings.append("No author email provided")
    
    if errors:
        raise click.ClickException("\n".join(errors))
    
    return {
        "manifest": manifest,
        "signature": signature,
        "warnings": warnings,
    }


def publish_to_catalog(
    package_path: Path,
    catalog_url: str,
    token: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Publish a package to the catalog.
    
    Returns:
        Response from the catalog API
    """
    # For now, this returns a mock response since the catalog
    # is not yet implemented. In production, this would use
    # requests to upload to the catalog API.
    
    manifest = load_package_manifest(package_path)
    plugin_info = manifest.get("plugin", manifest)
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "Dry run - package would be published",
            "plugin_id": plugin_info.get("id"),
            "version": plugin_info.get("version"),
            "catalog_url": catalog_url,
        }
    
    # In production, this would be:
    # response = requests.post(
    #     urljoin(catalog_url, "/plugins/publish"),
    #     files={"package": open(package_path, "rb")},
    #     headers={"Authorization": f"Bearer {token}"} if token else {},
    # )
    # return response.json()
    
    # For now, return a placeholder indicating GitHub workflow
    return {
        "success": False,
        "message": (
            "Direct catalog publishing is not yet available. "
            "Please submit your plugin via GitHub pull request to: "
            "https://github.com/voicestudio/plugin-catalog"
        ),
        "plugin_id": plugin_info.get("id"),
        "version": plugin_info.get("version"),
        "instructions": [
            "1. Fork the plugin-catalog repository",
            "2. Add your .vspkg and .sig files to plugins/<plugin-id>/",
            "3. Update plugins/catalog.json with your plugin metadata",
            "4. Submit a pull request for review",
        ],
    }


def generate_submission_files(
    package_path: Path,
    output_dir: Path,
) -> Dict[str, Path]:
    """
    Generate files needed for catalog submission.
    
    Creates a directory structure suitable for PR submission.
    """
    manifest = load_package_manifest(package_path)
    plugin_info = manifest.get("plugin", manifest)
    plugin_id = plugin_info.get("id", "unknown")
    
    # Create output directory
    plugin_dir = output_dir / plugin_id.replace(".", "-")
    plugin_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy package
    import shutil
    pkg_dest = plugin_dir / package_path.name
    shutil.copy(package_path, pkg_dest)
    
    # Copy signature if exists
    sig_path = package_path.with_suffix(package_path.suffix + ".sig")
    sig_dest = None
    if sig_path.exists():
        sig_dest = plugin_dir / sig_path.name
        shutil.copy(sig_path, sig_dest)
    
    # Generate catalog entry
    catalog_entry = {
        "id": plugin_info.get("id"),
        "name": plugin_info.get("name"),
        "version": plugin_info.get("version"),
        "description": plugin_info.get("description", ""),
        "author": plugin_info.get("author", {}),
        "type": plugin_info.get("type", "custom"),
        "category": plugin_info.get("category", "custom"),
        "tags": plugin_info.get("catalog", {}).get("tags", []),
        "package_url": f"plugins/{plugin_id.replace('.', '-')}/{package_path.name}",
        "signature_url": f"plugins/{plugin_id.replace('.', '-')}/{sig_path.name}" if sig_dest else None,
    }
    
    entry_path = plugin_dir / "catalog-entry.json"
    with open(entry_path, "w", encoding="utf-8") as f:
        json.dump(catalog_entry, f, indent=2)
    
    return {
        "package": pkg_dest,
        "signature": sig_dest,
        "catalog_entry": entry_path,
        "directory": plugin_dir,
    }


@click.command("publish")
@click.argument(
    "package",
    type=click.Path(exists=True),
)
@click.option(
    "--catalog",
    default=DEFAULT_CATALOG_URL,
    help="Catalog URL to publish to.",
)
@click.option(
    "--token",
    envvar="VOICESTUDIO_CATALOG_TOKEN",
    help="Authentication token (or set VOICESTUDIO_CATALOG_TOKEN).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Validate without actually publishing.",
)
@click.option(
    "--no-signature",
    is_flag=True,
    help="Allow publishing without signature (not recommended).",
)
@click.option(
    "--prepare-submission",
    is_flag=True,
    help="Generate files for GitHub PR submission.",
)
@click.option(
    "--submission-output",
    type=click.Path(),
    default="./submission",
    help="Output directory for submission files.",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON.",
)
@click.pass_context
def publish_command(
    ctx: click.Context,
    package: str,
    catalog: str,
    token: Optional[str],
    dry_run: bool,
    no_signature: bool,
    prepare_submission: bool,
    submission_output: str,
    output_json: bool,
) -> None:
    """
    Publish a plugin to the VoiceStudio catalog.
    
    Uploads a signed .vspkg package to the plugin catalog for
    distribution. Requires the package to be signed unless
    --no-signature is specified.
    
    The recommended flow is to use --prepare-submission to generate
    files for a GitHub PR to the plugin-catalog repository.
    
    Examples:
    
        # Validate package for publishing
        voicestudio-plugin publish my-plugin-1.0.0.vspkg --dry-run
        
        # Prepare files for GitHub submission
        voicestudio-plugin publish my-plugin-1.0.0.vspkg --prepare-submission
        
        # Publish directly (when API is available)
        voicestudio-plugin publish my-plugin-1.0.0.vspkg --token $TOKEN
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)
    
    package_path = Path(package).resolve()
    
    # Validate package
    try:
        validation = validate_package_for_publish(
            package_path,
            require_signature=not no_signature,
        )
    except click.ClickException:
        raise
    
    # Show warnings
    if validation.get("warnings") and not quiet and not output_json:
        click.echo(click.style("Warnings:", fg="yellow"))
        for warning in validation["warnings"]:
            click.echo(click.style(f"  [!] {warning}", fg="yellow"))
        click.echo()
    
    manifest = validation["manifest"]
    plugin_info = manifest.get("plugin", manifest)
    
    if not quiet and not output_json:
        click.echo(f"Publishing: {plugin_info.get('name')} v{plugin_info.get('version')}")
        click.echo(f"Plugin ID: {plugin_info.get('id')}")
        if validation.get("signature"):
            click.echo("Signature: [OK] Valid")
        click.echo()
    
    # Prepare submission mode
    if prepare_submission:
        output_dir = Path(submission_output)
        files = generate_submission_files(package_path, output_dir)
        
        if output_json:
            click.echo(json.dumps({
                "success": True,
                "mode": "prepare_submission",
                "directory": str(files["directory"]),
                "files": {
                    "package": str(files["package"]),
                    "signature": str(files["signature"]) if files["signature"] else None,
                    "catalog_entry": str(files["catalog_entry"]),
                },
            }))
        else:
            if not quiet:
                click.echo(click.style("[OK] Submission files prepared", fg="green"))
                click.echo(f"  Directory: {files['directory']}")
                click.echo()
                click.echo("Next steps:")
                click.echo("  1. Fork https://github.com/voicestudio/plugin-catalog")
                click.echo(f"  2. Copy {files['directory']} to plugins/")
                click.echo("  3. Update plugins/catalog.json")
                click.echo("  4. Submit a pull request")
        
        return
    
    # Publish to catalog
    result = publish_to_catalog(
        package_path,
        catalog,
        token=token,
        dry_run=dry_run,
    )
    
    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            if dry_run:
                click.echo(click.style("[OK] Dry run successful", fg="green"))
                click.echo("  Package is valid and ready for publishing.")
            else:
                click.echo(click.style("[OK] Published successfully", fg="green"))
        else:
            click.echo(click.style("Publishing not yet available", fg="yellow"))
            click.echo()
            click.echo(result.get("message", ""))
            
            if result.get("instructions"):
                click.echo()
                click.echo("To submit your plugin:")
                for instruction in result["instructions"]:
                    click.echo(f"  {instruction}")
            
            click.echo()
            click.echo("Or use --prepare-submission to generate files:")
            click.echo(f"  voicestudio-plugin publish {package} --prepare-submission")
