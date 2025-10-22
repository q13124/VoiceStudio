# Dependency Management with pip-tools

VoiceStudio uses `pip-tools` for reliable dependency management and reproducible builds.

## Overview

- **requirements.in**: Human-readable dependency specifications
- **requirements.txt**: Locked dependencies with exact versions (auto-generated)
- **CI Integration**: Automated dependency locking validation

## Usage

### Adding Dependencies

1. Edit `requirements.in` to add new packages:
   ```ini
   # Add new dependency
   new-package>=1.0.0,<2.0.0
   ```

2. Regenerate locked requirements:
   ```bash
   pip-compile requirements.in
   ```

3. Commit both files:
   ```bash
   git add requirements.in requirements.txt
   git commit -m "Add new-package dependency"
   ```

### Installing Dependencies

```bash
# Install from locked requirements
pip install -r requirements.txt

# Or install in development mode
pip install -r requirements.in
```

### Updating Dependencies

```bash
# Update all dependencies to latest compatible versions
pip-compile --upgrade requirements.in

# Update specific package
pip-compile --upgrade-package package-name requirements.in
```

## CI Integration

The GitHub Actions workflow automatically:

1. **Validates** that `requirements.txt` is up-to-date with `requirements.in`
2. **Fails** the build if dependencies are out of sync
3. **Uploads** the locked requirements as an artifact

### Manual CI Check

```bash
# Check if requirements.txt is current
pip-compile --dry-run requirements.in
```

## Best Practices

### Dependency Specifications

- Use **compatible release** specifiers: `package>=1.0.0,<2.0.0`
- Avoid **exact pins** in `requirements.in` unless necessary
- Group related dependencies with comments

### Version Constraints

```ini
# Good: Compatible release
fastapi>=0.104.0,<1.0.0

# Avoid: Exact pin (unless required)
fastapi==0.104.0

# Good: Multiple constraints
uvicorn[standard]>=0.24.0,<1.0.0
```

### Security Updates

```bash
# Check for security vulnerabilities
pip-audit

# Update vulnerable packages
pip-compile --upgrade-package vulnerable-package requirements.in
```

## File Structure

```
VoiceStudio/
├── requirements.in          # Source dependencies
├── requirements.txt         # Locked dependencies (auto-generated)
├── .github/workflows/
│   └── dependency-lock.yml  # CI validation
└── docs/
    └── pip-tools-usage.md   # This documentation
```

## Troubleshooting

### Common Issues

1. **Conflicting Dependencies**
   ```bash
   # Check for conflicts
   pip-compile --dry-run requirements.in
   ```

2. **Outdated Lock File**
   ```bash
   # Force regeneration
   rm requirements.txt
   pip-compile requirements.in
   ```

3. **CI Failures**
   - Ensure `requirements.txt` is committed after running `pip-compile`
   - Check that `requirements.in` changes are properly formatted

### Debug Commands

```bash
# Show dependency resolution
pip-compile --verbose requirements.in

# Check what would change
pip-compile --dry-run requirements.in

# Show dependency tree
pipdeptree
```

## Migration from requirements.txt

If migrating from a traditional `requirements.txt`:

1. **Extract** version constraints to `requirements.in`
2. **Remove** exact pins, use compatible releases
3. **Generate** new locked requirements
4. **Test** installation in clean environment

```bash
# Example migration
echo "fastapi>=0.104.0,<1.0.0" > requirements.in
pip-compile requirements.in
pip install -r requirements.txt
```
