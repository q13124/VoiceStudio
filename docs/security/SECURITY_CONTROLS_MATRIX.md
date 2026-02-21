# Security Controls Matrix

**Phase 7 Sprint 3**  
**VoiceStudio Quantum+**

Maps security controls to implementation artifacts.

| Control | Implementation | Location |
|---------|----------------|----------|
| Auth (API key, JWT) | Auth middleware | `backend/api/middleware/auth_middleware.py` |
| Role-based authorization | `require_auth_if_enabled`, role checks | `backend/api/middleware/auth_middleware.py` |
| Secrets storage | Secrets vault | `backend/security/secrets_vault.py` |
| API key encryption | Fernet encryption | `backend/api/routes/api_key_manager.py` |
| API key persistence | JSON file store | `backend/services/api_key_store.py` |
| Security headers | CSP, HSTS, X-Frame-Options | `backend/api/middleware/security_headers.py` |
| Request signing | HMAC validation | `backend/api/middleware/request_signing.py` |
| Rate limiting | Per-IP rate limits | `backend/api/middleware/rate_limit.py` |
| Input validation | Pydantic validation | All route models |
| Audit logging | Auth logger, plugin lifecycle | `backend/security/audit_logger.py` |
| Plugin sandbox | Resource limits, isolation | `backend/plugins/sandbox.py` |
| Plugin signing | Ed25519 verification | `backend/plugins/supply_chain/signer.py` |
| SBOM generation | `sbom.yml` workflow | `.github/workflows/sbom.yml` |
| CVE monitoring | `security-monitor.yml` | `.github/workflows/security-monitor.yml` |
| Dependency scanning | pip-audit, Bandit, NuGet | CI workflows |

## Control Categories

- **Authentication**: API key, JWT, Windows Credential Manager (C#)
- **Authorization**: Role-based, resource-level
- **Data protection**: Encryption at rest (API keys), secrets vault
- **Network**: Security headers, CORS, rate limiting
- **Supply chain**: Plugin signing, SBOM, vulnerability scanning
