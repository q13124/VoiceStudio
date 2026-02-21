# Dependency Audit Report

**Date:** 2026-02-21  
**Phase 7 Sprint 3**  
**Tools:** pip-audit, dotnet list package --vulnerable

## Python Dependencies (pip-audit)

| Package | Version | Advisory ID | Fix Version |
|---------|---------|-------------|-------------|
| basicsr | 1.4.2 | GHSA-86w8-vhw6-q9qq | No fix |
| filelock | 3.19.1 | GHSA-w853-jp5j-5j7f | 3.20.1 |
| filelock | 3.19.1 | GHSA-qmgc-5h2g-mvrw | 3.20.3 |
| keras | 3.10.0 | Multiple (6) | 3.11.0+ |
| pillow | 11.3.0 | GHSA-cfh3-3jmp-rvhc | 12.1.1 |
| python-multipart | 0.0.20 | GHSA-wp53-j4wj-2cfg | 0.0.22 |
| transformers | 4.46.2 | Multiple (14) | 4.48.0+ |

**Total:** 25 known vulnerabilities in 6 packages.

### Risk Assessment

- **basicsr**: SLURM-specific (irrelevant for desktop app)
- **filelock, python-multipart**: Fix versions available; upgrade when possible
- **keras, transformers, pillow**: ML libraries; CVEs require loading untrusted models/files
- **Context**: VoiceStudio is offline-first desktop app; attack surface is limited

### VS-0046 Status

Per QUALITY_LEDGER and ADR-041: Python 3.11.9 runtime resolves many CVEs. Remaining CVEs are in ML libraries or have low exploitability for desktop use case.

## .NET Dependencies

Run `dotnet list package --vulnerable --include-transitive` in CI to capture NuGet vulnerability status.

## Recommendations

1. Upgrade filelock, python-multipart, pillow when compatible
2. Monitor keras/transformers for fix versions compatible with engine runtime
3. Accept basicsr CVE as documented risk (no fix, low severity)
