# Engine Proof Stream Status (Master Plan Phase 4)

**Date:** 2026-01-29  
**Owner:** Role 5 (Engine Engineer)  
**Traceability:** Optional & Available Tasks Master Plan — Phase 4 Engine Stream; [OPTIONAL_TASK_INVENTORY](../../governance/OPTIONAL_TASK_INVENTORY.md) §2.1, §3.1; [ENGINE_VENV_ISOLATION_SPEC](../../design/ENGINE_VENV_ISOLATION_SPEC.md)

This document records the **engine venv + baseline proofs** stream status: what is complete, what is blocked, and how to run proofs when prerequisites are met.

---

## 1. Prerequisites

| Prerequisite | Description | Status |
|--------------|-------------|--------|
| Backend on 8001 | `uvicorn backend.api.main:app --port 8001` from repo root (or `.venv` with backend deps) | Required for baseline proof |
| .venv | Python venv with `requests`, engine/backend deps; for XTTS: `COQUI_TOS_AGREED=1` | Required |
| Chatterbox (optional) | For Chatterbox proof: per [ENGINE_VENV_ISOLATION_SPEC](../../design/ENGINE_VENV_ISOLATION_SPEC.md) Option C, separate `.venv_chatterbox` with torch>=2.6 + chatterbox-tts | Blocked (TD-001) until dual venv or compatibility |

---

## 2. Baseline Proof Commands

| Engine | Command | Expected | Evidence |
|--------|---------|----------|----------|
| XTTS | `python scripts/baseline_voice_workflow_proof.py --engine xtts` | Exit 0; `audio_id` in proof_data.json; SLO-6 met with `--strict-slo` | `.buildlogs/proof_runs/baseline_workflow_<timestamp>/proof_data.json` |
| Piper | `python scripts/baseline_voice_workflow_proof.py --engine piper` | Exit 1 with HTTP 422 (Piper does not support voice cloning) or success if used for TTS-only path | Proof dir captured |
| Chatterbox | `python scripts/baseline_voice_workflow_proof.py --engine chatterbox` | Exit 0 + `audio_id` when Chatterbox venv is active and package installed | Blocked by TD-001 (torch 2.6 vs 2.2) until per-engine venv |

---

## 3. Venv Isolation (TD-001)

Per [ENGINE_VENV_ISOLATION_SPEC](../../design/ENGINE_VENV_ISOLATION_SPEC.md):

- **Option C (dual venv)**: Default `.venv` for XTTS/current stack; `.venv_chatterbox` for Chatterbox (torch 2.6+). Engine manifest for Chatterbox to specify `venv_path`/`python_path`; runtime uses that interpreter when starting the engine subprocess.
- **Verification**: When Option C is implemented, run `baseline_voice_workflow_proof.py --engine chatterbox` and confirm exit 0 and `audio_id` in proof_data.json.
- **Current**: Chatterbox baseline proof is **blocked**; XTTS and Piper paths are **available** when backend is running.

---

## 4. Stream Completion Criteria (Plan Phase 4)

- [x] Document engine proof stream status and prerequisites (this document).
- [x] XTTS baseline proof evidenced (TASK-0013 Complete; `.buildlogs/proof_runs/baseline_workflow_<timestamp>/proof_data.json` when backend on 8001). Re-run when needed: `python scripts/baseline_voice_workflow_proof.py --engine xtts`.
- [ ] Implement Option C venv isolation and run Chatterbox proof (Phase 6+ or when prioritized; TD-001).

---

## 5. References

- [ENGINE_ENGINEER_NEXT_TASKS_2026-01-28.md](ENGINE_ENGINEER_NEXT_TASKS_2026-01-28.md) §3, §9
- [TECH_DEBT_REGISTER](../../governance/TECH_DEBT_REGISTER.md) TD-001
- [ENGINE_VENV_ISOLATION_SPEC](../../design/ENGINE_VENV_ISOLATION_SPEC.md)
- [scripts/baseline_voice_workflow_proof.py](../../../scripts/baseline_voice_workflow_proof.py)
