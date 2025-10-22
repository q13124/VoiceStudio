# Lockfile Workflow (pip-tools)

This document describes the deterministic dependency management workflow for VoiceStudio using `pip-tools`.

## Files

- `requirements.in` — Direct dependencies (what we explicitly want)
- `requirements.txt` — Pinned dependencies (generated from requirements.in)
- `requirements.lock.txt` — Lockfile with transitive dependencies + hashes (generated)
- `constraints.txt` — Optional upper/lower bounds (additive constraints)

## Workflow

### 1. Add Dependencies

To add a new dependency:

```bash
# Add to requirements.in
echo "new-package>=1.0.0" >> requirements.in

# Regenerate requirements.txt
pip-compile requirements.in
```

### 2. Generate Lockfile

#### Linux/macOS
```bash
./tooling/lock/generate_lock.sh
```

#### Windows PowerShell
```powershell
.\tooling\lock\generate_lock.ps1
```

#### Manual
```bash
pip-compile --generate-hashes --output-file requirements.lock.txt requirements.in
```

### 3. Install Dependencies

#### Development (fast)
```bash
pip install -r requirements.txt
```

#### Production (secure)
```bash
pip install -r requirements.lock.txt
```

## CI/CD Integration

The GitHub Actions workflow automatically:

1. ✅ Validates `requirements.txt` is up to date
2. 🔒 Generates `requirements.lock.txt` with hashes
3. 📦 Uploads lockfile as artifact

## Benefits

- **Deterministic builds**: Same versions across environments
- **Security**: Hash verification prevents supply chain attacks
- **Speed**: `requirements.txt` for fast dev installs
- **Reproducibility**: `requirements.lock.txt` for exact production builds

## Commands Reference

```bash
# Check if requirements.txt needs updating
pip-compile --check requirements.in

# Update requirements.txt
pip-compile requirements.in

# Generate lockfile with hashes
pip-compile --generate-hashes --output-file requirements.lock.txt requirements.in

# Install from lockfile
pip install -r requirements.lock.txt

# Sync virtual environment
pip-sync requirements.lock.txt
```

## Troubleshooting

### Lockfile conflicts
```bash
# Update lockfile
pip-compile --upgrade --generate-hashes --output-file requirements.lock.txt requirements.in
```

### Hash verification failures
```bash
# Regenerate with fresh hashes
pip-compile --generate-hashes --output-file requirements.lock.txt requirements.in
```

### Outdated requirements.txt
```bash
# Update requirements.txt
pip-compile requirements.in
git add requirements.txt
git commit -m "Update requirements.txt"
```
