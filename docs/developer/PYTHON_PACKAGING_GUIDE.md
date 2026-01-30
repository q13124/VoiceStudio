# Python Packaging Guide for VoiceStudio

**Purpose**: Prevent `ModuleNotFoundError` and import failures through proper Python package structure.  
**Audience**: All contributors working with Python code  
**Related**: [CONTRIBUTING.md](../../CONTRIBUTING.md#python-package-structure)

---

## Why Package Structure Matters

### The Critical Incident (2026-01-29)

**What Happened**: Missing `__init__.py` in `tools/overseer/agent/` caused all Overseer CLI commands to fail.

**Root Cause**: Python requires `__init__.py` to treat directories as packages. Without it:
```python
from tools.overseer.agent.identity import AgentRole  # ❌ ModuleNotFoundError
```

**Impact**: All governance tooling blocked (`gate status`, `ledger validate`, verification scripts).

**Prevention**: This guide + automated validation (pre-commit hooks, CI, tests).

---

## Python Package Requirements

### Rule 1: Every Package Directory Needs `__init__.py`

**Requirement**: If a directory contains `.py` files and you want to import from it, it MUST have `__init__.py`.

**Examples**:

```
✅ CORRECT:
tools/
├── __init__.py
├── overseer/
│   ├── __init__.py
│   ├── models.py
│   └── agent/
│       ├── __init__.py          ← REQUIRED
│       └── identity.py

❌ WRONG:
tools/
├── __init__.py
├── overseer/
│   ├── __init__.py
│   ├── models.py
│   └── agent/
│       └── identity.py          ← Missing __init__.py!
```

### Rule 2: `__init__.py` Can Be Empty

The simplest valid `__init__.py`:

```python
# Empty __init__.py
```

Or with a docstring:

```python
"""Agent governance module."""
```

### Rule 3: `__init__.py` Can Re-Export for Convenience

```python
"""Agent governance module."""

from .identity import AgentRole, AgentIdentity, AgentState
from .role_mapping import voicestudio_role_to_agent

__all__ = [
    "AgentRole",
    "AgentIdentity",
    "AgentState",
    "voicestudio_role_to_agent",
]
```

This allows:
```python
# Instead of:
from tools.overseer.agent.identity import AgentRole

# You can do:
from tools.overseer.agent import AgentRole
```

---

## Creating a New Python Module

### Step-by-Step Checklist

1. **Plan structure**
   ```
   tools/mymodule/
   ├── __init__.py
   ├── core.py
   └── utils.py
   ```

2. **Create directory**
   ```bash
   mkdir tools/mymodule
   ```

3. **Create `__init__.py` FIRST**
   ```bash
   echo '"""My module."""' > tools/mymodule/__init__.py
   ```

4. **Create implementation files**
   ```bash
   # Create core.py, utils.py, etc.
   ```

5. **Test import immediately**
   ```bash
   python -c "import tools.mymodule"
   python -c "from tools.mymodule.core import MyClass"
   ```

6. **Run validation**
   ```bash
   python scripts/validate_package_structure.py
   python scripts/validate_imports.py
   ```

7. **Commit atomically**
   ```bash
   git add tools/mymodule/
   git commit -m "feat(tools): add mymodule package"
   ```

### Anti-Pattern: What NOT to Do

```
❌ BAD (causes breakage):
1. Create tools/mymodule/core.py
2. Add import to existing code: from tools.mymodule.core import MyClass
3. Forget to create __init__.py
4. Imports break

✅ GOOD:
1. Create tools/mymodule/__init__.py (empty)
2. Create tools/mymodule/core.py
3. Test: python -c "from tools.mymodule.core import MyClass"
4. Add imports to existing code
5. Test again
6. Commit
```

---

## Validation Tools

### 1. Package Structure Validator

**Command**: `python scripts/validate_package_structure.py`

**What it checks**:
- Every directory with `.py` files has `__init__.py`
- Excludes: venv, external, build artifacts

**When to run**:
- Before committing (automatic via pre-commit hook)
- After creating new directories
- When debugging import errors

### 2. Import Validator

**Command**: `python scripts/validate_imports.py`

**What it checks**:
- Critical modules can be imported (`tools.overseer`, `backend.api.main`, `app.core.engines`, etc.)
- No `ModuleNotFoundError` or `ImportError`

**When to run**:
- Before committing (automatic via pre-commit hook)
- After modifying imports
- When adding new modules

### 3. Uncommitted Dependency Auditor

**Command**: `python scripts/audit_uncommitted_dependencies.py`

**What it checks**:
- Tracked files don't import from untracked modules
- Prevents broken imports from uncommitted code

**When to run**:
- Before committing (automatic via pre-commit hook)
- Before pushing
- When creating new modules that others will import

---

## Pre-Commit Hooks

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

### What Runs Automatically

On every `git commit`:
1. **Package structure validation** - Checks for missing `__init__.py`
2. **Import validation** - Ensures critical modules import successfully
3. **Uncommitted dependency audit** - Prevents broken import dependencies
4. **Ruff linting** - Python code quality
5. **Black formatting** - Code formatting
6. **Secret scanning** - Prevents accidental secret commits

### Bypassing (Emergency Only)

```bash
# Skip specific hooks
SKIP=python-import-check,package-structure-check git commit -m "message"

# Skip all hooks (NOT RECOMMENDED)
git commit --no-verify -m "message"
```

**Warning**: Only bypass in emergencies. Broken imports will fail in CI.

---

## Common Package Structure Patterns

### Pattern 1: Simple Package

```
mypackage/
├── __init__.py
└── core.py
```

```python
# __init__.py
"""My package."""

from .core import MyClass

__all__ = ["MyClass"]
```

### Pattern 2: Nested Package

```
mypackage/
├── __init__.py
├── core.py
└── subpackage/
    ├── __init__.py
    └── utils.py
```

```python
# mypackage/__init__.py
"""My package."""

from .core import MyClass
from .subpackage import MyUtil

# mypackage/subpackage/__init__.py
"""Subpackage."""

from .utils import MyUtil
```

### Pattern 3: Empty `__init__.py` (Namespace Package)

```
mypackage/
├── __init__.py          # Empty or just docstring
├── module_a.py
└── module_b.py
```

Import as:
```python
from mypackage.module_a import FunctionA
from mypackage.module_b import FunctionB
```

---

## Troubleshooting Import Errors

### Error: `ModuleNotFoundError: No module named 'tools.overseer.agent'`

**Cause**: Missing `__init__.py` in `tools/overseer/agent/`

**Fix**:
```bash
echo '"""Agent governance."""' > tools/overseer/agent/__init__.py
python -c "from tools.overseer.agent import identity"  # Test
```

### Error: `ImportError: cannot import name 'MyClass'`

**Causes**:
1. `MyClass` doesn't exist in the module
2. Circular import
3. `__init__.py` doesn't re-export `MyClass`

**Fix**:
```python
# In module.py
class MyClass:  # Ensure class exists
    pass

# In __init__.py (if re-exporting)
from .module import MyClass
```

### Error: `ImportError: attempted relative import with no known parent package`

**Cause**: Running a module as a script that uses relative imports.

**Fix**: Use `-m` flag:
```bash
# Bad:
python tools/overseer/cli/main.py

# Good:
python -m tools.overseer.cli.main
```

---

## CI/CD Integration

### Import Validation Job

Every PR runs import validation before tests:

```yaml
validate-imports:
  name: Validate Python Imports
  runs-on: windows-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
    - run: python scripts/validate_imports.py
    - run: python scripts/validate_package_structure.py
```

**Result**: Broken imports cannot merge to `master`.

---

## Testing Strategy

### Import Tests

**File**: `tests/unit/tools/overseer/test_imports.py`

```python
def test_overseer_agent_package_exists():
    """Regression test: Verify agent/__init__.py exists."""
    from pathlib import Path
    init_file = Path("tools/overseer/agent/__init__.py")
    assert init_file.exists(), "Missing __init__.py would break imports!"
```

**Purpose**: Smoke test that packages can be imported. Catches structural issues early.

---

## Best Practices

### ✅ DO

- Create `__init__.py` before implementation files
- Test imports after creating new modules
- Run validation scripts before committing
- Use pre-commit hooks
- Commit packages atomically

### ❌ DON'T

- Skip `__init__.py` ("I'll add it later")
- Add imports before creating `__init__.py`
- Bypass pre-commit hooks without reason
- Import from untracked modules
- Assume "it works on my machine"

---

## Quick Reference

### Validation Commands

```bash
# Validate package structure
python scripts/validate_package_structure.py

# Validate imports
python scripts/validate_imports.py

# Audit uncommitted dependencies
python scripts/audit_uncommitted_dependencies.py

# Run all verification
python scripts/run_verification.py
```

### Pre-Commit Setup

```bash
pip install pre-commit
pre-commit install
```

### Creating New Package

```bash
mkdir -p tools/mymodule
echo '"""My module."""' > tools/mymodule/__init__.py
# Create other files
python -c "import tools.mymodule"  # Test
git add tools/mymodule/
git commit -m "feat(tools): add mymodule"
```

---

## Reference

- **ADR-017**: Debug Role Architecture (incident that motivated this guide)
- **Incident Report**: `docs/reports/verification/DEBUG_ROLE_COMPLETE_INTEGRATION_2026-01-29.md`
- **Prevention Plan**: `.cursor/plans/critical_breakage_prevention_plan_*.plan.md`
- **Python Docs**: https://docs.python.org/3/tutorial/modules.html#packages
