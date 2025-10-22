# VoiceStudio — Integrated Execution Map

*Last updated: 2025-10-22 (America/Chicago)*

## 0) Purpose

Single, authoritative view that unifies:

* **Overseer** operating model (ChatGPT TL + Project Overseer)
* **Agents & Workers** automation strategy
* **Handshake** (ChatGPT ↔ Cursor) free automation loop
* **Day-by-Day Roadmap** interface for Cursor-ready drops
* **Professional UI/UX spec** alignment with backend

Use this map as the top-level "START HERE" for development and ops.

---

## 1) High-Level System Overview (C4-ish)

```
[User]
  │
  │  (prompts / requests)
  ▼
[ChatGPT Overseer + Tech Lead]
  │  ├─ Generates Day-X plans (Cursor-ready)
  │  └─ Writes CURSOR_EXECUTE blocks → docs/HANDSHAKE_STATUS.md
  ▼
[Handshake Repo]
  │  └─ Source of truth for instructions + results
  ▼
[Cursor Auto-Executor (.cursor/auto_execute.py)]
  │  ├─ Runs every 15 min via Task Scheduler
  │  ├─ Reads latest CURSOR_EXECUTE Block N
  │  ├─ Executes commands (build/test/codegen)
  │  └─ Appends CURSOR_RESULTS Block N to handshake
  ▼
[VoiceStudio Codebase]
  ├─ services/ (FastAPI, APIs)
  ├─ workers/ (agents, generation/processing/training workers)
  ├─ web/ (React UI)
  ├─ tests/ (E2E/units)
  └─ docs/ (handshake, specs, roadmaps)

Runtime (Requests):
Client (Web/UI) → API Gateway/Router → Orchestrator → Worker Pool
  → Engines (XTTS/OpenVoice/…)
  → Processing (denoise/EQ/LUFS) → Storage/Cache → Response Stream
```

---

## 2) Control Plane & Loops

### 2.1 Overseer Control Loop

* **Inputs**: Roadmap status, CURSOR_RESULTS blocks, metrics.
* **Process**: Select next Day-X slice → emit **Cursor-ready plan** → write **CURSOR_EXECUTE Block N**.
* **Outputs**: Commits/tests/code patches executed by Cursor; new metrics.

### 2.2 Handshake Automation Loop (free)

1. ChatGPT writes **CURSOR_EXECUTE Block N** → `docs/HANDSHAKE_STATUS.md`.
2. Cursor task runs each 15 min → executes commands → appends **CURSOR_RESULTS Block N**.
3. ChatGPT reads results → plans **Block N+1**.

### 2.3 Runtime Orchestration Loop

* API → Orchestrator → routing to **Generation Workers (GPU)** or **Processing Workers (CPU)**.
* **Quality Monitor Agent** intercepts pre/post generation.
* **Performance Agent** preloads/unloads models & tunes batch sizes.
* **A/B Agent** funnels traffic for experiments.
* **Training Agent** performs off-peak fine-tuning (nightly).

---

## 3) Module Map (Files ⇄ Responsibilities)

### 3.1 Overseer & Planning (ChatGPT-side outputs)

* `CHATGPT_INSTRUCTIONS.md` → Day-by-Day plan spec + response format.
* `CHATGPT_PROJECT_OVERSEER_GUIDE.md` → Prompts/templates for planning, reviews, sprints.

**Deliverable Form**:

```
# Day X: Feature Name
File: path/to/file.py
[full code]
Install: pip install ...
Test: pytest ...
Expected: short
```

### 3.2 Agents & Workers (Code)

* `workers/agents/quality_monitor_agent.py` → score, auto-regenerate, learn engine prefs.
* `workers/agents/performance_agent.py` → model preload/unload, batch sizing, cache.
* `workers/agents/training_agent.py` → nightly LoRA/finetune, deploy/rollback.
* `workers/agents/data_collector_agent.py` → pull public data, transcribe, filter.
* `workers/agents/ab_testing_agent.py` → experiments, significance, deploy winners.
* `workers/orchestrator.py` → wires agents + worker loops.
* `workers/generation_worker.py` → GPU engines (XTTS/OpenVoice/…)
* `workers/processing_worker.py` → CPU mastering (denoise/EQ/LUFS/convert).
* `workers/training_worker.py` → GPU training jobs.

### 3.3 UI/UX & API

* `PROFESSIONAL_VOICE_CLONER_SPEC.md` → screens, controls, UX behaviors.
* `services/api/*` (to implement) → REST + WebSocket streaming.
* `web/*` → React: drag-drop upload, generation panel, library, presets, A/B.

### 3.4 Automation & Ops

* `FREE_HANDSHAKE_AUTOMATION.md` → `.cursor/auto_execute.py`, scheduler PS script.
* `docs/HANDSHAKE_STATUS.md` → bi-directional instruction log.

---

## 4) Data & Control Flows

### 4.1 Generation Request Flow

```
UI → POST /v1/text-to-speech { text, voice_id, settings }
  → API Router → Orchestrator
    → QualityAgent.preprocess(req)
    → Select Worker (GPU availability, routing policy)
      → Engine gen (XTTS/OpenVoice/…)
    → Processing (Mastering pipeline: denoise→EQ→DRC→LUFS→de-ess→limit)
    → QualityAgent.validate(out)
    → Cache + Return (optionally stream via WS)
```

### 4.2 Learning/Improvement Flow (nightly)

```
Ratings/metrics → TrainingAgent.collect → LoRA fine-tune → A/B gate
  → If improved → Deploy → PerformanceAgent preload → record
  → Else → Rollback
```

### 4.3 A/B & Routing Intelligence

* **A/B Agent** runs controlled experiments.
* **Quality Agent** persists failure patterns → **Engine preferences** per language/text length/noise.
* **Performance Agent** updates preload/unload and batch sizes.

---

## 5) Execution Tracks (Roadmap ↔ Code Targets)

### Track A — Week 1 (Foundation)

1. Fix CI/GitHub Actions (Py 3.11).
2. Multi-reference fusion embeddings.
3. Quality scoring + auto-regeneration.
4. Audio mastering pipeline.
5. Voice settings interface (stability/clarity/etc.).
6. Minimal Web UI (drag-drop).
7. Voice library (save/load).

### Track B — Week 2 (Pro)

8. Engine router.
9. Batch processing (100+).
10. Model caching.
11. Emotion control.
12. Voice designer.
13. WebSocket streaming.
14. REST API surface.

### Track C — Week 3 (Agents)

15–21. All agents + Master Orchestrator wired in.

### Track D — Week 4 (Polish)

22–28. Pro UI, marketplace, tests, docs, perf, security, deploy.

> Each day produces a **Cursor-ready Day-X plan** that edits/creates specific files and includes `Install`, `Test`, `Expected`.

---

## 6) Minimal Contracts & Interfaces

### 6.1 Orchestrator ⇄ Agents

```python
class OrchestratorContracts:
    # preprocess(request) → possibly altered request
    # validate(output) → possibly altered output or retry directive
    pass
```

### 6.2 Worker Job Schema (concept)

```json
{
  "id": "uuid",
  "type": "generate|master|convert|denoise|train",
  "payload": { "text": "...", "voice_id": "...", "settings": {"stability":0.75,...} },
  "priority": 5,
  "deadline": null
}
```

### 6.3 Quality Score Envelope

```json
{
  "similarity": 0.0-100.0,
  "clarity": 0.0-100.0,
  "lufs": -16.0,
  "flags": ["clip", "dc_offset", "silence_head"]
}
```

---

## 7) Handshake: Working Blocks

### 7.1 Template — New Instruction Block

```
CURSOR_EXECUTE Block {N}:
# keep commands idempotent, short, testable
pytest -q
python -c "print('handshake ok')"
```

### 7.2 Result Sample

```
CURSOR_RESULTS Block {N} [YYYY-MM-DD HH:MM]:
✓ pytest -q
  Output: 112 passed
✓ python -c "print('handshake ok')"
  Output: handshake ok
```

---

## 8) UI ↔ Backend Alignment (from Pro Spec)

* **Instant Clone**: Fast embedding → voice profile saved → immediately usable.
* **Generation Panel**: stability/clarity/style/speaker-boost → mapped to engine params.
* **Emotion Control**: prosody transforms → exposed via `EmotionController`.
* **Audio Mastering**: standardized chain; defaults at -16 LUFS; flags to UI.
* **A/B Panel**: blind compare + rating → writes to metrics store → training queue.

---

## 9) Environments & Ops

* **CI**: Python 3.11 runner; cache models if possible.
* **Scheduler (Windows)**: Task runs `.cursor/auto_execute.py` every 15 min.
* **Artifacts**: `docs/HANDSHAKE_STATUS.md` is the single log of truth.
* **Security**: No secrets needed for free loop; repo permissions standard.

---

## 10) Next Concrete Actions

1. Seed `web/` with **Blind A/B panel** and wire to `/api/ab/submit`.
2. Land **Quality Scorer** minimal version and expose `/api/quality/score`.
3. Add **Engine Router** shim in orchestrator, reading QualityAgent prefs.
4. Initialize `docs/HANDSHAKE_STATUS.md` and start **Block 1–3** sanity tasks.

**Block 1 (example)**

```
CURSOR_EXECUTE Block 1:
python --version
pytest -q || echo "tests pending"
```

**Block 2 (example)**

```
CURSOR_EXECUTE Block 2:
python -m pip install -U pip
pip install resemblyzer
python -c "from resemblyzer import VoiceEncoder; print('OK')"
```

**Block 3 (example)**

```
CURSOR_EXECUTE Block 3:
python - <<'PY'
from pathlib import Path
p=Path('docs/HANDSHAKE_HEALTH.txt'); p.write_text('OK')
print(p.read_text())
PY
```

---

## 11) Definition of Done (per feature slice)

* Code merged + tests passing in CI
* Day-X plan delivered & executed
* UI visible change or API measurable output
* Metrics recorded (perf/quality)
* Handshake shows ✓ results

---

## 12) Governance & Guardrails (short form)

* **SemVer** for all packages/plugins
* **Idempotent** CURSOR_EXECUTE blocks
* **No breaking API** without migration
* **Tests** before enablement in router
* **A/B** gate for risky changes
* **Rollback** path for models and code

---

## 13) Appendix: Mappings to Source Files

* Strategy: `AI_AGENTS_WORKERS_STRATEGY.md`
* Overseer Ops: `CHATGPT_PROJECT_OVERSEER_GUIDE.md`
* TL Mode & Daily Plan: `CHATGPT_INSTRUCTIONS.md`
* UI & UX: `PROFESSIONAL_VOICE_CLONER_SPEC.md`
* Automation: `FREE_HANDSHAKE_AUTOMATION.md`

```text
This document is the canonical integration map. Keep updated alongside code.
```
