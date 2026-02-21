# Incident Response Playbook

**Phase 7 Sprint 3**  
**VoiceStudio Quantum+**

## 1. Credential Leak

**Symptoms:** API key or token exposed in logs, repo, or public artifact.

**Immediate actions:**
1. Rotate the credential immediately (revoke, generate new)
2. Update `config/api-keys.json` and `.env.mcp.local` (do not commit)
3. If in git history: use `git filter-repo` or BFG to remove; force-push (coordinate with team)
4. Audit all systems that used the credential

**Prevention:**
- Never commit secrets; use `config/api-keys.json` (gitignored)
- Use `api_key_encryption.key` for API key encryption

**Owner:** Security / Release Engineer

---

## 2. Malicious Plugin

**Symptoms:** Plugin crashes host, exfiltrates data, or violates sandbox.

**Immediate actions:**
1. Disable plugin via Plugin Management panel or `backend/plugins/gallery/installer`
2. Uninstall plugin
3. Review plugin manifest and source; verify signature
4. If plugin was from marketplace: flag for review queue; notify publisher
5. Document in QUALITY_LEDGER

**Prevention:**
- Plugin sandbox with resource limits
- Ed25519 signing verification
- SBOM and provenance checks before install

**Owner:** Core Platform / Plugin maintainer

---

## 3. Data Breach

**Symptoms:** User data (audio, profiles, projects) exposed or unauthorized access.

**Immediate actions:**
1. Isolate affected systems; revoke access
2. Identify scope (what data, which users)
3. Notify affected users if required
4. Preserve logs for forensic analysis
5. Document in QUALITY_LEDGER; create incident report

**Prevention:**
- Local-first; no cloud storage by default
- File validation (magic bytes) before processing
- Least-privilege file system access

**Owner:** Security / Release Engineer

---

## 4. Build/Supply Chain Compromise

**Symptoms:** Build artifact tampering, dependency poisoning.

**Immediate actions:**
1. Halt releases; do not distribute new builds
2. Verify build provenance (commit, CI run)
3. Run `pip-audit` and `dotnet list package --vulnerable`
4. Rebuild from clean checkout; verify checksums
5. Document in QUALITY_LEDGER

**Prevention:**
- SBOM generation in CI
- Dependency pinning; Dependabot
- Build provenance (Phase 7)

**Owner:** Build & Tooling Engineer

---

## Escalation

- **Blocking/critical:** Update STATE.md; escalate to Overseer
- **HIGH PRIORITY:** Add to Next 3 Steps
