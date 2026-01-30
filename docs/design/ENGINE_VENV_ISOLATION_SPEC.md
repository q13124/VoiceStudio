# Engine Venv Isolation Spec (TD-001)

> **Version**: 1.0  
> **Last Updated**: 2026-01-30  
> **Owner**: Role 5 (Engine Engineer)  
> **Status**: ACTIVE  
> **Traceability**: [TECH_DEBT_REGISTER](../governance/TECH_DEBT_REGISTER.md) TD-001; [OPTIONAL_TASK_INVENTORY](../governance/OPTIONAL_TASK_INVENTORY.md) §2.1

This document specifies the per-engine or dual-venv strategy to resolve Chatterbox engine torch>=2.6 dependency conflict with XTTS (torch 2.2.2+cu121).

---

## 1. Problem Statement

**Issue**: Chatterbox engine requires `torch>=2.6` (via `chatterbox-tts` package). Current venv uses `torch 2.2.2+cu121` for XTTS compatibility. Installing Chatterbox in the same venv causes dependency conflict or breaks XTTS.

**Impact**: Chatterbox voice cloning unavailable; baseline proof fails.

**Source**: [TASK-0009](../tasks/TASK-0009.md), [TASK-0010](../tasks/TASK-0010.md), [TECH_DEBT_REGISTER](../governance/TECH_DEBT_REGISTER.md) TD-001.

---

## 2. Options

### Option A: Upgrade torch to 2.6+ for All Engines

**Pros**: Single venv; simpler.  
**Cons**: Risk to XTTS (torch 2.6 compatibility unknown); requires XTTS re-validation.  
**Recommendation**: **Not recommended** unless XTTS is verified compatible with torch 2.6.

### Option B: Downgrade Chatterbox or Use Alternative

**Pros**: Keep torch 2.2.2+cu121.  
**Cons**: Chatterbox may not support torch 2.2.x; alternative engines may not match Chatterbox capabilities.  
**Recommendation**: **Not recommended** unless Chatterbox releases torch 2.2.x-compatible version.

### Option C: Dual Venv (Per-Engine Isolation) [RECOMMENDED]

**Pros**: Isolates torch versions; XTTS and Chatterbox can coexist.  
**Cons**: More complex; requires runtime to select venv per engine.  
**Recommendation**: **Recommended** — safe isolation without breaking XTTS.

---

## 3. Recommended Approach: Option C (Dual Venv)

### 3.1 Venv Structure

- **Default venv**: `.venv` — torch 2.2.2+cu121, XTTS, Piper, and other engines compatible with torch 2.2.x.
- **Chatterbox venv**: `.venv_chatterbox` — torch>=2.6, chatterbox-tts.

### 3.2 Engine Manifest Extension

Add `venv_path` or `python_path` to Chatterbox engine manifest (`engines/chatterbox.json`):

```json
{
  "engine_id": "chatterbox",
  "engine_name": "Chatterbox",
  "python_path": ".venv_chatterbox/Scripts/python.exe",
  ...
}
```

### 3.3 Runtime Changes

**File**: `app/core/runtime/runtime_engine_enhanced.py` (or `runtime_engine.py`)

**Action**: When starting an engine subprocess, check if engine manifest has `python_path` or `venv_path`; use that interpreter instead of default.

**Example**:

```python
# In start_engine() or similar
python_exe = engine_manifest.get("python_path", sys.executable)
subprocess.Popen([python_exe, "-m", "app.core.engines.chatterbox_engine", ...])
```

### 3.4 Verification

- **Setup**: Create `.venv_chatterbox` with `python -m venv .venv_chatterbox`; activate; `pip install torch>=2.6 chatterbox-tts`.
- **Test**: Run `python scripts/baseline_voice_workflow_proof.py --engine chatterbox`; expect exit 0 and `audio_id` in proof_data.json.
- **Regression**: Re-run XTTS baseline proof; confirm no regression.

---

## 4. Alternative: Venv Families (Future)

For more engines with conflicting deps, extend to **venv families**:

- `.venv_torch22` — XTTS, Piper, etc.
- `.venv_torch26` — Chatterbox, future engines
- `.venv_tf` — TensorFlow-based engines

Engine manifest specifies `venv_family`; runtime maps to venv path.

---

## 5. Exit Criteria

- [ ] Dual venv strategy implemented (`.venv` and `.venv_chatterbox`)
- [ ] Engine manifest extended with `python_path` or `venv_path`
- [ ] Runtime uses engine-specific interpreter when starting subprocess
- [ ] Chatterbox baseline proof PASS (exit 0, `audio_id` in proof_data.json)
- [ ] XTTS baseline proof PASS (no regression)
- [ ] TD-001 closed in TECH_DEBT_REGISTER

---

## 6. References

- [TECH_DEBT_REGISTER](../governance/TECH_DEBT_REGISTER.md) TD-001
- [OPTIONAL_TASK_INVENTORY](../governance/OPTIONAL_TASK_INVENTORY.md) §2.1
- [ENGINE_ENGINEER_NEXT_TASKS_2026-01-28](../reports/verification/ENGINE_ENGINEER_NEXT_TASKS_2026-01-28.md) §3
