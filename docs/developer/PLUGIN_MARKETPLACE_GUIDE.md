# VoiceStudio Plugin Marketplace Guide

Guide to submitting, managing, and distributing plugins through the VoiceStudio Gallery.

## Overview

The VoiceStudio Gallery is the official marketplace for discovering, installing, and managing plugins. Publishers can distribute plugins for free or commercially, with automated security scanning and quality checks.

## Publisher Registration

### Requirements

Before publishing plugins, you need a Publisher account:

1. **Individual Developer**: Personal account for hobby or open-source plugins
2. **Verified Publisher**: Verified organization for commercial plugins
3. **Enterprise Publisher**: For enterprise-scale distribution

### Registration Process

1. Go to [gallery.voicestudio.app/publishers](https://gallery.voicestudio.app/publishers)
2. Sign in with your VoiceStudio account
3. Complete the publisher profile
4. Agree to the Publisher Agreement
5. For Verified Publisher: Complete identity verification

### Publisher Profile

```yaml
Publisher Information:
  - Display Name: Your Company Name
  - Publisher ID: com.yourcompany
  - Website: https://yourcompany.com
  - Support Email: support@yourcompany.com
  - Logo: 256x256 PNG
  - Description: Brief company/developer description
```

## Submission Process

### 1. Prepare Your Plugin

Ensure your plugin meets the requirements:

```bash
# Validate manifest and structure
voicestudio-plugin validate --strict

# Run tests with coverage
voicestudio-plugin test --coverage

# Check security (recommended)
voicestudio-plugin security-check
```

### 2. Create Package

```bash
# Create distributable package
voicestudio-plugin pack

# Sign the package (required for publication)
voicestudio-plugin sign my-plugin-1.0.0.vspkg --key signing-key.pem
```

### 3. Prepare Listing

Create compelling marketplace listing content:

**Required:**
- Plugin icon (256x256 PNG)
- Short description (100 chars max)
- Full description (Markdown)
- At least one screenshot
- Category selection

**Recommended:**
- Demo video/GIF
- Detailed changelog
- Support documentation
- Example usage

### 4. Submit for Review

```bash
# Submit to marketplace
voicestudio-plugin publish --draft

# Or via web interface
# Upload at gallery.voicestudio.app/publish
```

## Review Process

### Automated Checks

All submissions undergo automated validation:

| Check | Description | Time |
|-------|-------------|------|
| Manifest | Schema validation | < 1 min |
| Security | Malware and vulnerability scan | 5-10 min |
| Dependencies | License and version checks | 2-5 min |
| Signature | Cryptographic verification | < 1 min |
| Build | Clean build verification | 5-15 min |

### Manual Review

After automated checks pass, reviewers evaluate:

| Criteria | Description |
|----------|-------------|
| Functionality | Plugin works as described |
| Quality | Code quality and stability |
| Security | Security best practices |
| UX | User experience and documentation |
| Policy | Compliance with policies |

### Review Timeline

| Type | Expected Time |
|------|---------------|
| New Plugin | 3-5 business days |
| Update (minor) | 1-2 business days |
| Update (major) | 2-3 business days |
| Security Fix | 1 business day |

### Review Outcomes

| Result | Description | Action |
|--------|-------------|--------|
| **Approved** | Ready for publication | Auto-publish or manual release |
| **Needs Changes** | Minor issues found | Fix and resubmit |
| **Rejected** | Policy violation | Appeal or significant revision |

## Marketplace Listing

### Listing Requirements

**Icon**
- Size: 256x256 pixels
- Format: PNG with transparency
- No text or badges

**Screenshots**
- Minimum: 1, Maximum: 10
- Size: 1280x720 or larger
- Show actual plugin functionality

**Description**
```markdown
# Short Description (100 chars)
A brief, compelling summary of what your plugin does.

# Full Description
## Features
- Feature 1
- Feature 2

## Requirements
- VoiceStudio 2.0+
- Windows 10/11

## Getting Started
Quick start guide...

## Support
Contact support@example.com
```

### Categories

Select the most appropriate category:

| Category | Description |
|----------|-------------|
| Synthesis | Text-to-speech engines |
| Transcription | Speech-to-text engines |
| Effects | Audio effects and filters |
| Enhancement | Audio quality improvement |
| Analysis | Audio analysis tools |
| Utilities | General utilities |
| Integration | Third-party integrations |

### Tags

Add relevant tags (up to 10):

```
tts, synthesis, neural, streaming, multilingual, gpu, realtime
```

## Pricing and Distribution

### Pricing Models

| Model | Description | Commission |
|-------|-------------|------------|
| Free | No cost to users | 0% |
| Freemium | Free + paid features | 15% on paid |
| Paid | One-time purchase | 15% |
| Subscription | Recurring payment | 15% |

### Setting Prices

```yaml
Pricing:
  model: paid
  price: 29.99
  currency: USD
  regional_pricing:
    EU: 27.99 EUR
    UK: 24.99 GBP
  discounts:
    - type: launch
      percent: 20
      expires: 2024-02-01
```

### Free Trial

```yaml
Trial:
  enabled: true
  duration: 14  # days
  features: full  # or "limited"
```

## Updates and Versions

### Version Numbering

Follow semantic versioning:

```
MAJOR.MINOR.PATCH

1.0.0  # Initial release
1.0.1  # Bug fix
1.1.0  # New feature
2.0.0  # Breaking change
```

### Release Channels

| Channel | Purpose | Auto-Update |
|---------|---------|-------------|
| `stable` | Production releases | Yes (by default) |
| `beta` | Testing new features | Opt-in |
| `alpha` | Early development | Opt-in |

### Publishing Updates

```bash
# Publish update to stable
voicestudio-plugin publish --notes CHANGELOG.md

# Publish to beta channel
voicestudio-plugin publish --channel beta

# Staged rollout (10% initially)
voicestudio-plugin publish --rollout 10
```

### Changelog Best Practices

```markdown
## [1.1.0] - 2024-01-15

### Added
- New voice model: "Emma"
- Batch processing support

### Changed
- Improved synthesis quality
- Reduced memory usage

### Fixed
- Fixed crash on long texts
- Fixed audio artifacts at boundaries

### Security
- Updated dependencies
```

## Analytics and Insights

### Available Metrics

| Metric | Description |
|--------|-------------|
| Downloads | Total and daily downloads |
| Active Users | 7-day, 30-day active |
| Revenue | If paid/subscription |
| Ratings | Average and distribution |
| Crashes | Crash reports |
| Usage | Feature usage stats |

### Analytics Dashboard

Access at: `gallery.voicestudio.app/publisher/analytics`

```
Plugin: My TTS Plugin

Last 30 Days:
- Downloads: 1,234
- Active Users: 856
- Avg Rating: 4.7 ★
- Revenue: $2,450

Top Regions:
1. United States (42%)
2. Germany (15%)
3. United Kingdom (12%)
```

## User Reviews and Support

### Responding to Reviews

Best practices:
- Respond promptly to negative reviews
- Be professional and constructive
- Offer solutions, not excuses
- Thank users for positive feedback

```markdown
# Example Response

Thank you for your feedback! We apologize for the issue you
experienced with voice loading times. This has been fixed
in version 1.2.1. Please update and let us know if you
continue to experience any problems.

- Your Company Support Team
```

### Support Integration

```yaml
Support:
  email: support@example.com
  documentation: https://docs.example.com/my-plugin
  issues: https://github.com/example/my-plugin/issues
  discord: https://discord.gg/example
```

## Policy Compliance

### Content Policy

**Prohibited:**
- Malware or malicious code
- Privacy-violating functionality
- Copyright-infringing content
- Hate speech or harmful content
- Deceptive functionality

### Technical Requirements

| Requirement | Description |
|-------------|-------------|
| Manifest v4 | Use manifest schema v4 |
| Signed | Valid cryptographic signature |
| Tested | Pass automated tests |
| Documented | User documentation required |
| Support | Active support channel |

### Privacy Requirements

If your plugin collects data:

```yaml
Privacy:
  data_collection: true
  privacy_policy: https://example.com/privacy
  data_types:
    - usage_analytics
    - crash_reports
  data_sharing: none
  gdpr_compliant: true
```

## Troubleshooting

### Common Rejection Reasons

| Reason | Resolution |
|--------|------------|
| Invalid manifest | Fix validation errors |
| Security issues | Address security findings |
| Inadequate testing | Add more test coverage |
| Missing documentation | Add required docs |
| Policy violation | Review and comply |

### Appeal Process

1. Review rejection feedback
2. Make necessary changes
3. Submit appeal with explanation
4. Wait for re-review (3-5 days)

### Getting Help

- Documentation: [docs.voicestudio.app/marketplace](https://docs.voicestudio.app/marketplace)
- Forum: [forum.voicestudio.app/plugins](https://forum.voicestudio.app/plugins)
- Email: [marketplace@voicestudio.app](mailto:marketplace@voicestudio.app)
- Discord: [discord.gg/voicestudio](https://discord.gg/voicestudio)

## Checklist

Before submitting, verify:

### Plugin Quality
- [ ] All tests pass
- [ ] Coverage > 80%
- [ ] No security vulnerabilities
- [ ] Documentation complete

### Package
- [ ] Manifest valid (v4 schema)
- [ ] Package signed
- [ ] Checksums valid
- [ ] Dependencies declared

### Listing
- [ ] Icon (256x256 PNG)
- [ ] Screenshots (at least 1)
- [ ] Description (short + full)
- [ ] Category selected
- [ ] Tags added

### Legal
- [ ] Privacy policy (if collecting data)
- [ ] Terms of service
- [ ] License specified
- [ ] No IP violations

## See Also

- [Plugin Development Guide](./PLUGIN_DEVELOPMENT_GUIDE.md)
- [CLI Reference](./PLUGIN_CLI_REFERENCE.md)
- [Security Guide](./PLUGIN_SECURITY_GUIDE.md)
