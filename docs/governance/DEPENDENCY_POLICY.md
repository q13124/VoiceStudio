# Dependency Policy

> Version: 1.0.0 | Last Updated: 2026-02-05 | Owner: Core Platform Team

This document defines the policy for managing external dependencies in VoiceStudio, including security patching, update procedures, and governance.

---

## Table of Contents

1. [Security Patch SLA](#security-patch-sla)
2. [Automated Dependency Updates](#automated-dependency-updates)
3. [Review and Approval Workflow](#review-and-approval-workflow)
4. [Rollback Procedures](#rollback-procedures)
5. [Dependency Selection Criteria](#dependency-selection-criteria)
6. [Prohibited Dependencies](#prohibited-dependencies)
7. [Monitoring and Auditing](#monitoring-and-auditing)

---

## Security Patch SLA

Security vulnerabilities in dependencies must be addressed within the following timeframes:

| Severity | Response Time | Resolution Deadline | Escalation |
|----------|---------------|---------------------|------------|
| **Critical** (CVSS 9.0-10.0) | 4 hours | 24 hours | Immediate team notification |
| **High** (CVSS 7.0-8.9) | 24 hours | 7 days | Daily standup discussion |
| **Medium** (CVSS 4.0-6.9) | 7 days | 30 days | Sprint planning inclusion |
| **Low** (CVSS 0.1-3.9) | 30 days | 90 days | Backlog tracking |

### Response Actions

1. **Assess Impact**: Determine if the vulnerability affects VoiceStudio's usage of the dependency
2. **Identify Fix**: Check for patched version or workaround
3. **Test Fix**: Run full test suite against patched version
4. **Deploy**: Follow standard release process or hotfix if critical

---

## Automated Dependency Updates

VoiceStudio uses **GitHub Dependabot** for automated dependency updates.

### Configuration

- **Location**: `.github/dependabot.yml`
- **Schedule**: Weekly updates for non-security, immediate for security
- **PR Labels**: `dependencies`, ecosystem-specific labels

### Monitored Ecosystems

| Ecosystem | Directory | Schedule | Purpose |
|-----------|-----------|----------|---------|
| pip (Python) | `/` | Weekly | Backend dependencies |
| pip (Python) | `/backend` | Weekly | Backend-specific dependencies |
| nuget (.NET) | `/src` | Weekly | Frontend/Core dependencies |
| github-actions | `/` | Weekly | CI/CD workflow actions |

### Auto-merge Criteria

Dependabot PRs may be auto-merged when:

- [ ] All CI checks pass
- [ ] Update is patch-level (e.g., 1.2.3 → 1.2.4)
- [ ] No breaking changes documented
- [ ] Security update with no test failures

Minor and major version updates require manual review.

---

## Review and Approval Workflow

### Standard Dependency Updates

1. **Dependabot creates PR** with version bump
2. **CI runs tests** including security scans
3. **Developer reviews** changelog and breaking changes
4. **Approval required** from at least one team member
5. **Merge to main** after approval

### New Dependency Addition

Adding a new dependency requires additional scrutiny:

1. **Proposal**: Document why the dependency is needed
2. **Alternatives**: List alternatives considered
3. **License Check**: Verify license compatibility (see [Prohibited Dependencies](#prohibited-dependencies))
4. **Security Audit**: Check for known vulnerabilities
5. **Size Impact**: Assess impact on build size/time
6. **Approval**: Requires approval from System Architect role

### Review Checklist

- [ ] Changelog reviewed for breaking changes
- [ ] License remains compatible (MIT, Apache-2.0, BSD)
- [ ] No new security vulnerabilities introduced
- [ ] Test suite passes completely
- [ ] Documentation updated if API changes

---

## Rollback Procedures

### Immediate Rollback (Production Issues)

If a dependency update causes production issues:

1. **Revert the merge commit** that introduced the update
2. **Deploy the revert** following hotfix procedures
3. **Create an issue** documenting the failure
4. **Root cause analysis** before re-attempting update

```bash
# Example rollback command
git revert <merge-commit-sha>
git push origin main
```

### Delayed Rollback (Test Failures Discovered Later)

If issues are discovered after merge but before release:

1. **Pin to previous version** in requirements/csproj
2. **Create PR** with pinned version
3. **Document the issue** in the PR description
4. **Schedule investigation** for next sprint

### Version Pinning

When rollback is needed, pin exact versions:

```python
# requirements.txt - pin vulnerable version
package-name==1.2.3  # Pinned: v1.2.4 causes issue #123
```

```xml
<!-- csproj - pin vulnerable version -->
<PackageReference Include="Package.Name" Version="1.2.3" />
<!-- Pinned: v1.2.4 causes issue #123 -->
```

---

## Dependency Selection Criteria

### Required Criteria

All new dependencies MUST meet these requirements:

1. **License**: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, or ISC
2. **Maintenance**: Active maintenance (commit within last 12 months)
3. **Security**: No unpatched critical/high vulnerabilities
4. **Stability**: Stable release (not alpha/beta for production use)
5. **Cost**: Free and open-source (per `free-only.mdc` rule)

### Preferred Criteria

Dependencies SHOULD meet these preferences:

1. **Popularity**: Widely adopted in the ecosystem
2. **Documentation**: Comprehensive documentation available
3. **Testing**: Well-tested with good coverage
4. **Size**: Minimal footprint preferred
5. **Dependencies**: Minimal transitive dependencies

### Evaluation Template

When proposing a new dependency, provide:

```markdown
## Dependency Proposal: [package-name]

**Version**: x.y.z
**License**: [license]
**Repository**: [url]

### Purpose
Why is this dependency needed?

### Alternatives Considered
1. [Alternative 1] - Why not chosen
2. [Alternative 2] - Why not chosen

### Impact Assessment
- Build size impact: [minimal/moderate/significant]
- Transitive dependencies: [count]
- Security audit: [pass/issues]
```

---

## Prohibited Dependencies

### License Restrictions

The following licenses are NOT permitted:

- GPL (any version) - Copyleft requirement
- AGPL (any version) - Network copyleft
- SSPL - Service restriction
- Any commercial/proprietary license
- Any license requiring payment or seat-based licensing

### Known Problematic Packages

| Package | Reason | Alternative |
|---------|--------|-------------|
| *None currently* | | |

### Deprecated Dependencies

Dependencies marked for removal:

| Package | Deprecation Date | Removal Date | Replacement |
|---------|------------------|--------------|-------------|
| *None currently* | | | |

---

## Monitoring and Auditing

### Automated Scans

The following scans run automatically:

| Tool | Frequency | Purpose |
|------|-----------|---------|
| `pip-audit` | Every PR | Python vulnerability scan |
| `safety` | Every PR | Python vulnerability scan |
| NuGet Audit | Every PR | .NET vulnerability scan |
| `detect-secrets` | Every PR | Secret leak prevention |
| Dependabot | Weekly | Version updates |

### Manual Audits

Quarterly dependency audits include:

1. **SBOM Generation**: Full software bill of materials
2. **License Compliance**: Verify all licenses remain compliant
3. **Unused Dependencies**: Remove any unused packages
4. **Update Assessment**: Plan major version updates
5. **Security Review**: Review any deferred security updates

### Audit Artifacts

- **Location**: `.buildlogs/dependency-audit/`
- **Format**: JSON and Markdown reports
- **Retention**: 1 year

---

## References

- [SBOM Generation Script](../../scripts/generate_sbom.py)
- [CVE Monitoring Workflow](../../.github/workflows/security-monitor.yml)
- [Secrets Rotation Guide](../developer/SECRETS_ROTATION_GUIDE.md)
- [VoiceStudio Security Policy](./SECURITY_POLICY.md)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-05 | 1.0.0 | Initial policy creation |
