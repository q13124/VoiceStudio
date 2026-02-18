# Plugin Privacy Guide

This document explains VoiceStudio's privacy framework for plugin developers and how to comply with privacy requirements.

## Overview

VoiceStudio's privacy engine (Phase 6C) implements GDPR-inspired data protection principles:

1. **Purpose Limitation** - Data collected only for declared purposes
2. **Data Minimization** - Collect only what's necessary
3. **Transparency** - Clear disclosure of data practices
4. **User Rights** - Access, correction, deletion capabilities
5. **Security** - Appropriate protection measures

## Data Categories

| Category | Code | Description | Examples |
|----------|------|-------------|----------|
| Usage | `USAGE` | Feature usage patterns | Button clicks, feature adoption |
| Telemetry | `TELEMETRY` | Performance metrics | Response times, memory usage |
| Preferences | `PREFERENCES` | User settings | Theme, defaults, UI state |
| Content | `CONTENT` | User-generated data | Audio files, text, projects |
| Derived | `DERIVED` | Computed from other data | Trends, predictions, scores |
| System | `SYSTEM` | Device/environment info | OS version, GPU, CPU |

## Privacy Levels

| Level | Code | Description | Requirements |
|-------|------|-------------|--------------|
| Anonymous | `ANONYMOUS` | Cannot identify user | No consent needed |
| Pseudonymous | `PSEUDONYMOUS` | Indirect identification | Consent recommended |
| Personal | `PERSONAL` | Direct identification | Consent required |
| Sensitive | `SENSITIVE` | Special category data | Explicit consent, extra protections |
| Regulatory | `REGULATORY` | Subject to specific laws | Legal compliance required |

## Manifest Declaration

Declare your data practices in `manifest.json`:

```json
{
  "name": "my_plugin",
  "version": "1.0.0",
  "compliance": {
    "data_declaration": {
      "collects_usage_data": true,
      "collects_telemetry": true,
      "collects_personal_data": false,
      "data_categories": ["USAGE", "TELEMETRY"],
      "privacy_levels": ["ANONYMOUS"],
      "purpose": "Improve plugin performance and features",
      "retention_days": 90,
      "third_party_sharing": false
    },
    "privacy_policy_url": "https://example.com/privacy",
    "gdpr_compliant": true,
    "ccpa_compliant": true
  }
}
```

## Consent Management

### When Consent is Required

| Privacy Level | Consent Type |
|---------------|--------------|
| ANONYMOUS | Not required |
| PSEUDONYMOUS | Recommended (implied OK) |
| PERSONAL | Explicit opt-in required |
| SENSITIVE | Explicit + purpose-specific |
| REGULATORY | Per applicable law |

### Requesting Consent

```python
from backend.plugins.compliance.privacy_engine import PrivacyEngine

privacy = PrivacyEngine()

# Check existing consent
has_consent = privacy.check_consent(
    user_id="user123",
    plugin_id="my_plugin",
    data_category=DataCategory.USAGE,
    purpose="analytics"
)

# Request consent (triggers UI prompt)
if not has_consent:
    consent_id = privacy.request_consent(
        user_id="user123",
        plugin_id="my_plugin",
        data_categories=[DataCategory.USAGE, DataCategory.TELEMETRY],
        purpose="analytics",
        description="Help us improve by sharing anonymous usage data"
    )
```

### Recording Consent

```python
# When user grants consent
privacy.record_consent(
    user_id="user123",
    consent_id=consent_id,
    granted=True,
    timestamp=datetime.utcnow()
)
```

## User Rights

### Right to Access

Users can request their data:

```python
# Get all data held for a user
user_data = privacy.get_user_data(
    user_id="user123",
    plugin_id="my_plugin"
)
# Returns: {"data_categories": {...}, "consents": [...], ...}
```

### Right to Deletion

Users can request data erasure:

```python
# Delete all user data
privacy.delete_user_data(
    user_id="user123",
    plugin_id="my_plugin"
)
```

### Right to Portability

Export data in standard format:

```python
# Export in JSON format
export_data = privacy.export_user_data(
    user_id="user123",
    plugin_id="my_plugin",
    format="json"
)
```

## Data Storage

### Persistence

Privacy-related data is stored in:
- `{app_data}/voicestudio/phase6/privacy/consents/` - Consent records
- `{app_data}/voicestudio/phase6/privacy/declarations/` - Data declarations
- `{app_data}/voicestudio/phase6/privacy/requests/` - Access/deletion requests

### Encryption

All privacy data is encrypted at rest using AES-256.

### Retention

Honor declared retention periods:

```python
# Automatically delete data older than retention period
privacy.enforce_retention(plugin_id="my_plugin")
```

## Compliance Scanning

The compliance scanner checks your plugin for privacy issues:

```python
from backend.plugins.compliance.compliance_scanner import ComplianceScanner

scanner = ComplianceScanner()
report = scanner.scan_plugin(plugin_path)

# Check privacy findings
for finding in report.findings:
    if finding.category == "privacy":
        print(f"{finding.severity}: {finding.message}")
```

### Common Privacy Findings

| Finding | Severity | Description |
|---------|----------|-------------|
| Missing privacy policy URL | HIGH | Compliance section lacks privacy_policy_url |
| Undeclared data collection | HIGH | Code collects data not in declaration |
| Excessive data collection | MEDIUM | Collecting more than necessary |
| Missing retention period | MEDIUM | No retention_days specified |
| Third-party sharing unclear | LOW | No third_party_sharing declaration |

## Best Practices

### Do

- Declare all data collection in manifest
- Request only necessary data
- Provide clear privacy policy
- Honor deletion requests promptly
- Use anonymous/pseudonymous when possible
- Set reasonable retention periods
- Encrypt sensitive data

### Don't

- Collect data without declaration
- Share data with third parties silently
- Store data longer than necessary
- Ignore user consent preferences
- Use personal data for undisclosed purposes
- Skip privacy review for updates

## API Reference

### Privacy Engine Methods

```python
class PrivacyEngine:
    def register_plugin(self, plugin_id: str, declaration: PluginDataDeclaration) -> None
    def check_consent(self, user_id: str, plugin_id: str, ...) -> bool
    def request_consent(self, user_id: str, plugin_id: str, ...) -> str
    def record_consent(self, user_id: str, consent_id: str, granted: bool, ...) -> None
    def revoke_consent(self, user_id: str, plugin_id: str, ...) -> None
    def get_user_data(self, user_id: str, plugin_id: str) -> dict
    def delete_user_data(self, user_id: str, plugin_id: str) -> None
    def export_user_data(self, user_id: str, plugin_id: str, format: str) -> bytes
    def enforce_retention(self, plugin_id: str) -> int
```

### REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/privacy/consent` | POST | Record user consent |
| `/api/v1/privacy/consent/{plugin_id}` | GET | Get consent status |
| `/api/v1/privacy/consent/{plugin_id}` | DELETE | Revoke consent |
| `/api/v1/privacy/data/{plugin_id}` | GET | Export user data |
| `/api/v1/privacy/data/{plugin_id}` | DELETE | Delete user data |

## Related Documentation

- [Phase 6 Developer Guide](PHASE6_DEVELOPER_GUIDE.md)
- [ADR-039: Phase 6 Architecture](../architecture/decisions/ADR-039-phase6-strategic-maturity.md)
- [Plugin Manifest Schema](../../shared/schemas/plugin-manifest.schema.json)
