# VoiceStudio – Isolating Legacy TTS Engines (Architecture Recommendation)

> **Purpose:** handoff document for Cursor (implementation-focused).  
> **Goal:** run multiple legacy TTS engines (e.g., Tortoise, Bark, ElevenLabs-local, etc.) concurrently/on-demand **without** UI freezes, dependency conflicts, or memory bleed, while supporting hot-swapping and robust crash recovery.

---

## 1) Problem Summary

VoiceStudio is a PySide6/Qt desktop "studio-grade" app with heavy ML inference (GPU/CPU) and an information-dense, modular UI. Running multiple TTS engines in a single Python process causes:

- UI stalls when inference blocks the main thread (or starves event loop).
- Engine/library conflicts (global state, incompatible deps, CUDA/PyTorch collisions).
- Memory/VRAM bloat and fragmentation over time (models "never unload" cleanly).
- A single engine crash/hang can destabilize the whole app.

**We need:** concurrency + isolation + responsiveness + hot-swapping + recovery + memory-safety.

---

## 2) Core Decision (Recommended Architecture)

### ✅ Recommended: **Multi-process engine isolation** + **standard IPC contract**
**Each engine runs out-of-process** (its own OS process). The UI talks to engines via IPC (HTTP/JSON-RPC, sockets, pipes, or QProcess stdio protocol). This yields:

- **Hard isolation:** crashes/hangs stay contained to that engine process.
- **True parallelism:** bypasses GIL; multiple engines can run concurrently.
- **Memory safety:** when an engine process exits, OS releases RAM/VRAM reliably.
- **Hot-swapping:** start/stop/restart engines without restarting the UI.

**High-level components:**

1. **UI Process (PySide6):** only orchestration + rendering + UX.
2. **Engine Manager (Supervisor):** starts/stops engines, routes requests, watches health.
3. **Engine Worker Process (per engine):** loads model + runs synthesis/training tasks.
4. **IPC Layer:** sends requests, receives progress/results/errors.

---

## 3) Evaluated Approaches (Why This Wins)

### A) Threads only (QThread / Python threads)
- Prevents *some* UI freezes, but **no isolation**: memory leaks and crashes still bring down the whole app.
- GIL limits CPU parallelism for Python-heavy workloads.
- Doesn't solve dependency conflicts.

**Verdict:** Not sufficient for VoiceStudio's "multiple heavy engines" requirement.

### B) Docker/container per engine
- Strong environment isolation (separate deps, CUDA libs, etc.)
- Clean "engine as service" boundary

But:
- Requires Docker installation / extra UX burden.
- Harder local GPU setup and distribution.
- Adds operational complexity.

**Verdict:** Optional fallback if dependency conflicts are extreme; not first choice for desktop UX.

### C) Local HTTP/JSON-RPC wrappers (FastAPI/Flask)
- Great as the **IPC layer** / contract boundary.
- By itself, **not isolation** unless the server runs in a separate process.

**Verdict:** Excellent in combination with multi-process; not standalone.

### D) Multi-process subprocess/multiprocessing
- Best blend of stability + simplicity for desktop.
- The supervisor can terminate/restart an engine without killing the UI.

**Verdict:** Primary recommendation.

---

## 4) Concrete Reference Architecture

### 4.1 Process Model

- **One engine = one long-lived worker process** (default)
  - Minimizes duplicate model loads.
  - Stable latency (warm model).
- **Optional:** process pool for lightweight engines (CPU-only, small models).
- **GPU-heavy engines:** default to **single worker** to avoid VRAM duplication and OOM.

### 4.2 IPC Options (Pick One)

**Option 1 (Recommended for clarity): Local HTTP + JSON**
- Each engine worker runs a tiny FastAPI server bound to `127.0.0.1`.
- UI calls `POST /synthesize` and receives:
  - immediate `job_id`
  - progress via websocket or polling (`GET /jobs/{id}`)
  - result path to WAV or streamed bytes

Pros: clean contract, easy debugging, easy plugin onboarding.  
Cons: firewall edge cases; some overhead (usually negligible on localhost).

**Option 2: Sockets (ZeroMQ / raw TCP) with JSON-RPC**
- Faster than HTTP, no open HTTP server semantics.
- Good for local-only service.

Pros: efficient, robust.  
Cons: more bespoke plumbing.

**Option 3: Qt `QProcess` + stdin/stdout JSON lines protocol**
- UI uses `QProcess` to spawn engine script.
- Engine reads JSON commands from stdin; emits JSON events to stdout.

Pros: tight Qt integration; simple distribution.  
Cons: binary payloads awkward; recommended to return file paths for audio.

> **Practical note:** Regardless of IPC, return *audio file paths* (WAV/FLAC) instead of pushing large raw buffers through IPC. It simplifies memory and avoids base64 overhead.

---

## 5) Engine Manager / Supervisor Responsibilities

### 5.1 Lifecycle
- Start engine process on-demand (lazy) or at app startup (eager).
- Stop engine cleanly on app exit.
- Optionally auto-stop idle engines after N minutes.

### 5.2 Routing
- Map `engine_id` → process handle + IPC endpoint.
- Route each request to selected engine.

### 5.3 Queueing & Scheduling
- Per-engine queue for jobs when engine is busy.
- Global scheduling policy:
  - GPU-heavy engines: serialize jobs by default.
  - CPU engines: allow limited parallelism.
- Allow user-configurable "Max concurrent jobs" per engine.

### 5.4 Watchdog / Recovery
- Health checks (heartbeat):
  - `GET /health` (HTTP) or ping message (RPC)
- Hang detection:
  - if no progress update within timeout window → mark hung
- Restart strategy:
  - terminate process → spawn fresh instance → mark job failed or retry if safe
- Crash detection:
  - process exit code indicates crash → log + auto-restart (with backoff)

### 5.5 Observability
- Per-engine logs:
  - `logs/engine_<id>.log`
- UI log panel:
  - stream key events (job start/stop, errors, restarts)
- Diagnostics export:
  - include engine logs + version info + last N events

---

## 6) Job Protocol (Standard Contract)

Define a stable interface so engines become swappable plugins.

### 6.1 Synthesize Request (example schema)
```json
{
  "job_id": "uuid",
  "engine_id": "tortoise",
  "text": "Hello world",
  "voice_profile": "Tyler_Main",
  "language": "en",
  "params": {
    "speed": 1.0,
    "pitch": 0.0,
    "temperature": 0.7,
    "seed": 123
  },
  "output": {
    "format": "wav",
    "sample_rate": 48000,
    "path_hint": "…/output/job_uuid.wav"
  }
}
```

### 6.2 Progress Event (push)
```json
{
  "job_id": "uuid",
  "status": "running",
  "progress": 0.42,
  "stage": "decode_waveform",
  "message": "Generating candidate 2/5"
}
```

### 6.3 Completion Event
```json
{
  "job_id": "uuid",
  "status": "done",
  "result": {
    "audio_path": "…/output/job_uuid.wav",
    "duration_s": 7.9
  }
}
```

### 6.4 Error Event
```json
{
  "job_id": "uuid",
  "status": "error",
  "error": {
    "type": "OOM",
    "message": "CUDA out of memory",
    "suggestion": "Reduce batch size or run one GPU job at a time"
  }
}
```

### 6.5 Cancel
- UI sends cancel for `job_id`.
- Engine attempts graceful stop; if not possible, supervisor can terminate engine process (hard cancel).

---

## 7) GPU & Memory Strategy (Avoiding VRAM Disaster)

### 7.1 Default Rules
- One GPU-heavy engine process active per GPU at a time (serialize jobs).
- Do not spawn multiple workers for the same GPU-heavy engine unless user explicitly enables it and has VRAM headroom.

### 7.2 "Reclaim" Actions
- **Soft reclaim:** engine unloads model (if supported) and runs `torch.cuda.empty_cache()`
- **Hard reclaim (most reliable):** restart the engine process (guaranteed OS-level cleanup)

### 7.3 Safety Gates
Before starting a GPU job:
- check available VRAM (nvidia-smi or PyTorch stats)
- if below threshold, queue job and notify user

---

## 8) UX Requirements (Premium Studio Feel)

### 8.1 Non-blocking UI
- UI thread never waits synchronously for engine responses.
- Use signals/slots (Qt) to update progress and results.
- Keep interaction responsive across panels (waveform/spectrogram, timeline, etc.).

### 8.2 Feedback
- Immediate "job created" acknowledgment.
- Progress bars with stage labels.
- Per-job status (queued/running/done/error) in a job queue panel.

### 8.3 User Control
- Cancel jobs.
- "Restart Engine" button in Settings > Engines.
- Engine status indicators (running, idle, crashed, restarting).

### 8.4 Logging/Diagnostics
- Expose last N log lines per engine inside a Logs panel.
- Provide "Export Diagnostics Bundle" (zip) for debugging.

---

## 9) Suggested Build Plan for Cursor (Step-by-Step)

### Step 1 — Define the Engine API Contract
- Create schemas for request/progress/result/error.
- Create an `EngineAdapter` base class/interface in the core seam.

### Step 2 — Implement the Engine Manager
- Start/stop processes
- Route jobs
- Maintain job queue
- Watchdog timeouts + restarts
- Logging + events

### Step 3 — Implement IPC (choose one)
- Recommend starting with **QProcess + JSON lines** (lowest friction for Qt).
- Or start with **HTTP FastAPI per engine** if you prefer explicit contract.

### Step 4 — Implement One Engine Worker (Pilot)
- Pick one engine (e.g., Tortoise or Bark).
- Wrap it into a worker:
  - load model once
  - accept synth requests
  - emit progress
  - write WAV to disk
  - return path

### Step 5 — Wire UI
- Add Jobs panel (queue + progress)
- Add Engine Status panel (loaded/running)
- Provide Cancel/Restart controls

### Step 6 — Expand to Additional Engines
- Add Bark worker, Piper worker, etc.
- Each worker matches the same contract.

### Step 7 — Add Safety + Polish
- GPU/VRAM gates
- Backoff on repeated crashes
- Diagnostics export

---

## 10) Final Recommendation (What to Do Now)

**Do this:**  
- Implement **Engine Manager + per-engine worker processes** with a stable IPC contract.  
- Start with one pilot engine in a subprocess, prove progress updates + cancel + restart.  
- Standardize everything around `.md` specs and schemas so Cursor stays aligned.

**Avoid this:**  
- Don't run multiple heavy engines in one Python process.  
- Don't rely on threads alone for isolation.  
- Don't commit to Docker unless dependency conflicts force it.

---

## Appendix A — Quick "Decision Rules"

- If you need **maximum desktop reliability** → multi-process engine workers.
- If you need **hard dependency isolation** → consider Docker, but only if required.
- If you need **clean plugin interface** → add HTTP/JSON-RPC contract on top of multi-process.

---

## Appendix B — Notes for Cursor

- Keep engine processes **stateless from the UI perspective** (job requests contain needed params).
- Prefer output paths for audio results to avoid IPC bloat.
- Add watchdog timeouts and restart logic early (don't postpone).
- Make it easy to disable concurrency per engine to avoid VRAM OOM.

