"""
TLS Configuration.

Task 2.4.2: In-transit encryption enforcement.
Ensures TLS 1.3 for all connections.
"""

from __future__ import annotations

import logging
import ssl
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TLSConfig:
    """TLS configuration."""
    # Certificate paths
    cert_file: str | None = None
    key_file: str | None = None
    ca_file: str | None = None

    # TLS version
    min_version: str = "TLSv1.2"
    prefer_version: str = "TLSv1.3"

    # Cipher suites (TLS 1.3 suites are implicit)
    ciphers: str = "ECDHE+AESGCM:DHE+AESGCM:ECDHE+CHACHA20:DHE+CHACHA20"

    # Security options
    verify_client: bool = False
    check_hostname: bool = True

    # HSTS settings
    hsts_enabled: bool = True
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False


def create_ssl_context(config: TLSConfig) -> ssl.SSLContext:
    """
    Create an SSL context with secure defaults.

    Args:
        config: TLS configuration

    Returns:
        Configured SSLContext
    """
    # Use TLS 1.2+ by default
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # Set minimum version
    if config.min_version == "TLSv1.3":
        context.minimum_version = ssl.TLSVersion.TLSv1_3
    else:
        context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Prefer TLS 1.3
    context.maximum_version = ssl.TLSVersion.TLSv1_3

    # Set ciphers (for TLS 1.2)
    try:
        context.set_ciphers(config.ciphers)
    except ssl.SSLError as e:
        logger.warning(f"Could not set ciphers: {e}")

    # Load certificates
    if config.cert_file and config.key_file:
        context.load_cert_chain(config.cert_file, config.key_file)

    if config.ca_file:
        context.load_verify_locations(config.ca_file)

    # Client verification
    if config.verify_client:
        context.verify_mode = ssl.CERT_REQUIRED
    else:
        context.verify_mode = ssl.CERT_NONE

    # Disable insecure options
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_TLSv1
    context.options |= ssl.OP_NO_TLSv1_1

    # Enable forward secrecy
    context.options |= ssl.OP_SINGLE_DH_USE
    context.options |= ssl.OP_SINGLE_ECDH_USE

    logger.info(f"Created SSL context with min version: {config.min_version}")
    return context


def create_client_ssl_context(
    verify: bool = True,
    ca_file: str | None = None,
) -> ssl.SSLContext:
    """
    Create a client SSL context.

    Args:
        verify: Whether to verify server certificates
        ca_file: Optional CA bundle file

    Returns:
        Configured client SSLContext
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_3

    if verify:
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True

        if ca_file:
            context.load_verify_locations(ca_file)
        else:
            context.load_default_certs()
    else:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    return context


def get_hsts_header(config: TLSConfig) -> str:
    """
    Get HSTS header value.

    Args:
        config: TLS configuration

    Returns:
        HSTS header value string
    """
    if not config.hsts_enabled:
        return ""

    parts = [f"max-age={config.hsts_max_age}"]

    if config.hsts_include_subdomains:
        parts.append("includeSubDomains")

    if config.hsts_preload:
        parts.append("preload")

    return "; ".join(parts)


def enforce_tls(request_scheme: str, host: str) -> tuple[bool, str | None]:
    """
    Check if TLS is enforced for a request.

    Args:
        request_scheme: Request scheme (http/https)
        host: Request host

    Returns:
        (is_secure, redirect_url) tuple
    """
    if request_scheme == "https":
        return True, None

    # Don't redirect localhost in development
    if host in ("localhost", "127.0.0.1", "::1"):
        return True, None

    # Return redirect URL
    redirect_url = f"https://{host}"
    return False, redirect_url


def generate_self_signed_cert(
    output_dir: str,
    hostname: str = "localhost",
    days: int = 365,
) -> tuple[str, str]:
    """
    Generate a self-signed certificate for development.

    Args:
        output_dir: Directory to write cert files
        hostname: Certificate hostname
        days: Validity period

    Returns:
        (cert_path, key_path) tuple
    """
    from datetime import datetime, timedelta

    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    # Generate key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VoiceStudio Dev"),
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=days))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(hostname),
                x509.DNSName("localhost"),
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # Write files
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cert_path = output_path / "server.crt"
    key_path = output_path / "server.key"

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    logger.info(f"Generated self-signed cert: {cert_path}")
    return str(cert_path), str(key_path)
