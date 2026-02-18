"""
Plugin Sign Command.

Signs plugin packages using Ed25519 signatures.
"""

import base64
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import click


def check_cryptography_installed() -> bool:
    """Check if the cryptography library is installed."""
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519
        return True
    except ImportError:
        return False


def generate_keypair() -> Tuple[bytes, bytes]:
    """
    Generate a new Ed25519 keypair.
    
    Returns:
        Tuple of (private_key_bytes, public_key_bytes)
    """
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    
    return private_bytes, public_bytes


def load_private_key(key_path: Path) -> Any:
    """Load a private key from file."""
    from cryptography.hazmat.primitives.asymmetric import ed25519
    
    with open(key_path, "rb") as f:
        content = f.read()
    
    # Check if it's base64 encoded
    try:
        key_bytes = base64.b64decode(content)
    except Exception:
        key_bytes = content
    
    # Handle different formats
    if len(key_bytes) == 32:
        # Raw 32-byte key
        return ed25519.Ed25519PrivateKey.from_private_bytes(key_bytes)
    elif len(key_bytes) == 64:
        # Some tools store 64 bytes (private + public)
        return ed25519.Ed25519PrivateKey.from_private_bytes(key_bytes[:32])
    else:
        # Try PEM format
        from cryptography.hazmat.primitives import serialization
        try:
            return serialization.load_pem_private_key(content, password=None)
        except Exception:
            raise click.ClickException(
                "Invalid key format. Expected 32-byte Ed25519 private key."
            )


def sign_package(
    package_path: Path,
    private_key: Any,
) -> Dict[str, Any]:
    """
    Sign a package file.
    
    Returns:
        Signature metadata including the signature
    """
    # Read package content
    with open(package_path, "rb") as f:
        content = f.read()
    
    # Calculate checksum
    checksum = hashlib.sha256(content).hexdigest()
    
    # Sign the checksum
    signature_bytes = private_key.sign(checksum.encode("utf-8"))
    signature_b64 = base64.b64encode(signature_bytes).decode("ascii")
    
    # Get public key
    public_key = private_key.public_key()
    from cryptography.hazmat.primitives import serialization
    
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    public_b64 = base64.b64encode(public_bytes).decode("ascii")
    
    return {
        "format_version": "1.0",
        "signed_at": datetime.utcnow().isoformat() + "Z",
        "package_checksum": checksum,
        "checksum_algorithm": "sha256",
        "signature_algorithm": "ed25519",
        "signature": signature_b64,
        "public_key": public_b64,
    }


def verify_signature(
    package_path: Path,
    signature_path: Path,
    public_key_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """
    Verify a package signature.
    
    Returns:
        Tuple of (is_valid, message)
    """
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric import ed25519
    
    # Load signature file
    with open(signature_path, encoding="utf-8") as f:
        sig_data = json.load(f)
    
    # Read package content
    with open(package_path, "rb") as f:
        content = f.read()
    
    # Calculate checksum
    checksum = hashlib.sha256(content).hexdigest()
    
    # Verify checksum matches
    if sig_data.get("package_checksum") != checksum:
        return False, "Package checksum mismatch - file may have been modified"
    
    # Get public key
    if public_key_path:
        with open(public_key_path, "rb") as f:
            key_content = f.read()
        try:
            public_bytes = base64.b64decode(key_content)
        except Exception:
            public_bytes = key_content
    else:
        # Use embedded public key
        public_b64 = sig_data.get("public_key")
        if not public_b64:
            return False, "No public key in signature file and none provided"
        public_bytes = base64.b64decode(public_b64)
    
    # Load public key
    public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
    
    # Verify signature
    signature_b64 = sig_data.get("signature")
    if not signature_b64:
        return False, "No signature in signature file"
    
    signature_bytes = base64.b64decode(signature_b64)
    
    try:
        public_key.verify(signature_bytes, checksum.encode("utf-8"))
        return True, "Signature is valid"
    except InvalidSignature:
        return False, "Invalid signature"


@click.command("sign")
@click.argument(
    "package",
    type=click.Path(),
    required=False,
    default=None,
)
@click.option(
    "-k", "--key",
    type=click.Path(exists=True),
    help="Private key file for signing.",
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output signature file (default: <package>.sig).",
)
@click.option(
    "--generate-key",
    is_flag=True,
    help="Generate a new keypair.",
)
@click.option(
    "--key-output",
    type=click.Path(),
    default="plugin-signing.key",
    help="Output path for generated private key.",
)
@click.option(
    "--verify",
    "verify_flag",
    is_flag=True,
    help="Verify an existing signature instead of signing.",
)
@click.option(
    "--public-key",
    type=click.Path(exists=True),
    help="Public key file for verification (optional).",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON.",
)
@click.pass_context
def sign_command(
    ctx: click.Context,
    package: Optional[str],
    key: Optional[str],
    output: Optional[str],
    generate_key: bool,
    key_output: str,
    verify_flag: bool,
    public_key: Optional[str],
    output_json: bool,
) -> None:
    """
    Sign or verify a plugin package.
    
    Signs a .vspkg package using Ed25519 signatures. The signature
    can be verified by VoiceStudio to ensure package integrity.
    
    Examples:
    
        # Generate a new signing key
        voicestudio-plugin sign --generate-key
        
        # Sign a package
        voicestudio-plugin sign my-plugin-1.0.0.vspkg --key plugin-signing.key
        
        # Verify a signature
        voicestudio-plugin sign my-plugin-1.0.0.vspkg --verify
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)
    
    # Check cryptography is installed
    if not check_cryptography_installed():
        raise click.ClickException(
            "The 'cryptography' library is required for signing. "
            "Install it with: pip install cryptography"
        )
    
    # Generate keypair mode
    if generate_key:
        key_base = Path(key_output)
        
        # Use .private and .public extensions for clarity
        private_path = key_base.parent / f"{key_base.name}.private"
        public_path = key_base.parent / f"{key_base.name}.public"
        
        if private_path.exists():
            if not click.confirm(f"Key file {private_path} exists. Overwrite?"):
                raise click.ClickException("Aborted")
        
        private_bytes, public_bytes = generate_keypair()
        
        # Save private key
        private_b64 = base64.b64encode(private_bytes).decode("ascii")
        with open(private_path, "w", encoding="utf-8") as f:
            f.write(private_b64)
        
        # Save public key
        public_b64 = base64.b64encode(public_bytes).decode("ascii")
        with open(public_path, "w", encoding="utf-8") as f:
            f.write(public_b64)
        
        if output_json:
            click.echo(json.dumps({
                "success": True,
                "private_key": str(private_path),
                "public_key": str(public_path),
            }))
        else:
            if not quiet:
                click.echo(click.style("[OK] Keypair generated", fg="green"))
                click.echo(f"  Private key: {private_path}")
                click.echo(f"  Public key: {public_path}")
                click.echo()
                click.echo(click.style("[!] Keep your private key secure!", fg="yellow"))
                click.echo("  The public key can be shared for verification.")
        
        return
    
    # Package is required for sign and verify modes
    if not package:
        raise click.ClickException(
            "PACKAGE is required for signing or verification. "
            "Use --generate-key if you want to generate a new keypair."
        )
    
    package_path = Path(package).resolve()
    
    if not package_path.exists():
        raise click.ClickException(f"Package not found: {package_path}")
    
    # Verify mode
    if verify_flag:
        sig_path = package_path.with_suffix(package_path.suffix + ".sig")
        
        if not sig_path.exists():
            raise click.ClickException(f"Signature file not found: {sig_path}")
        
        public_key_path = Path(public_key) if public_key else None
        is_valid, message = verify_signature(package_path, sig_path, public_key_path)
        
        if output_json:
            click.echo(json.dumps({
                "valid": is_valid,
                "message": message,
                "package": str(package_path),
                "signature": str(sig_path),
            }))
        else:
            if is_valid:
                click.echo(click.style(f"[OK] {message}", fg="green"))
            else:
                click.echo(click.style(f"[X] {message}", fg="red"))
        
        if not is_valid:
            raise SystemExit(1)
        
        return
    
    # Sign mode
    if not key:
        raise click.ClickException(
            "Private key required for signing. "
            "Use --key to specify or --generate-key to create one."
        )
    
    key_path = Path(key)
    private_key = load_private_key(key_path)
    
    # Determine output path
    if output:
        sig_path = Path(output)
    else:
        sig_path = package_path.with_suffix(package_path.suffix + ".sig")
    
    if not quiet and not output_json:
        click.echo(f"Signing: {package_path.name}")
    
    # Sign the package
    sig_data = sign_package(package_path, private_key)
    
    # Write signature file
    with open(sig_path, "w", encoding="utf-8") as f:
        json.dump(sig_data, f, indent=2)
    
    if output_json:
        click.echo(json.dumps({
            "success": True,
            "package": str(package_path),
            "signature": str(sig_path),
            "checksum": sig_data["package_checksum"],
            "signed_at": sig_data["signed_at"],
        }))
    else:
        if not quiet:
            click.echo()
            click.echo(click.style("[OK] Package signed successfully", fg="green"))
            click.echo(f"  Signature: {sig_path}")
            click.echo(f"  Checksum: {sig_data['package_checksum'][:16]}...")
            click.echo()
            click.echo("To verify:")
            click.echo(f"  voicestudio-plugin sign {package_path} --verify")
