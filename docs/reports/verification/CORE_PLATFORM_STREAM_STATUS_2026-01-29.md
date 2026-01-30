# Core Platform Stream Status (Master Plan Phase 4)

**Date:** 2026-01-29  
**Owner:** Role 4 (Core Platform)  
**Traceability:** Optional & Available Tasks Master Plan — Phase 4 Core Platform Stream; [OPTIONAL_TASK_INVENTORY](../../governance/OPTIONAL_TASK_INVENTORY.md) §3.2; [ROLE_4_NEXT_TASKS_2026-01-28.md](ROLE_4_NEXT_TASKS_2026-01-28.md)

This document records the **wizard upload path + preflight checks** stream status for the optional tasks master plan.

---

## 1. Wizard Upload Path

| Item | Status | Evidence |
|------|--------|----------|
| Backend endpoint | **Aligned** | `POST /api/audio/upload` in [backend/api/routes/audio.py](../../../backend/api/routes/audio.py) — returns `{"audio_id": "upload_..."}` |
| Wizard proof script | **Aligned** | [scripts/wizard_flow_proof.py](../../../scripts/wizard_flow_proof.py) Step 1 calls `POST {backend_url}/api/audio/upload` with `file` (audio/wav); uses returned `audio_id` for validate/start steps |
| Voice cloning wizard | **Aligned** | [backend/api/routes/voice_cloning_wizard.py](../../../backend/api/routes/voice_cloning_wizard.py) uses `reference_audio_id` from upload; [voice.py](../../../backend/api/routes/voice.py) `_register_audio_file()` stores upload temp path by audio_id |

**Conclusion:** No code change required. Wizard upload path is aligned; run `python scripts/wizard_flow_proof.py --backend-url http://localhost:8001` when backend is on 8001 to capture full e2e proof (TASK-0020).

---

## 2. Preflight Live Check

| Check | Command | When | Evidence |
|-------|---------|------|----------|
| Preflight | `curl http://localhost:8001/api/health/preflight` | When backend running on 8001 | Record 200 response in STATE Session Log or Proof Index |
| Health | `curl http://localhost:8001/api/health` | Optional | Confirms backend reachable |

**Procedure:** Start backend (`uvicorn backend.api.main:app --port 8001` from repo root with `.venv` active), then run the curl command; document result in session handoff or Proof Index.

---

## 3. Stream Completion Criteria (Plan Phase 4)

- [x] Wizard upload endpoint or script alignment — **verified aligned** (upload path documented above).
- [x] Preflight live check — **procedure documented**; run when backend on 8001 and record result.

---

## 4. References

- [ROLE_4_NEXT_TASKS_2026-01-28.md](ROLE_4_NEXT_TASKS_2026-01-28.md) §2.2, §2.3
- [TASK-0020](../../tasks/TASK-0020.md) — Wizard flow e2e proof (blocked until backend on 8001)
- [scripts/README_WIZARD_PROOF.md](../../../scripts/README_WIZARD_PROOF.md)
