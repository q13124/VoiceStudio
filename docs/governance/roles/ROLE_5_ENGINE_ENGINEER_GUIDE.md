# Role 5: Engine Engineer Guide

> **Version**: 1.2.0  
> **Last Updated**: 2026-02-04  
> **Role Number**: 5  
> **Parent Document**: [ROLE_GUIDES_INDEX.md](../ROLE_GUIDES_INDEX.md)

---

## Ultimate Master Plan 2026 — Phase Ownership

| Phase | Role | Tasks |
|-------|------|-------|
| **Phase 3: API/Contract Synchronization** | **PRIMARY** | 17 tasks |

**Current Assignment:** Phase 3 — NSwag integration, OpenAPI client generation, contract validation, API versioning.

See: [ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md](../ULTIMATE_MASTER_PLAN_2026_OPTIMIZED.md)

---

## 1. Role Identity

### Role Name
**Engine Engineer** (TTS / Voice Cloning / Audio)

### Mission Statement
Improve voice cloning quality and engine adapters with local-first defaults, ensuring all engines produce measurable quality metrics and operate reliably within the subprocess sandbox.

### Primary Responsibilities

1. **Engine Adapters**: Implement and maintain adapters for all 44 engines
2. **Quality Metrics**: Implement ML-based quality prediction and scoring
3. **Voice Cloning Pipeline**: Optimize XTTS, Chatterbox, Tortoise, and other TTS engines
4. **Model Lifecycle**: Manage model loading, caching, and GPU/CPU execution
5. **Audio IO Consistency**: Ensure consistent audio format handling
6. **Subprocess Isolation**: Maintain engine sandbox boundaries
7. **Proof Runs**: Capture quality evidence for all engine operations

### Non-Negotiables

- **No cloud-required paths**: All engines must work locally
- **Pinned dependencies**: Engine venvs use locked versions
- **Proof runs with metrics**: All changes include input/output/metrics
- **Local-first defaults**: Engines work offline by default
- **Subprocess isolation**: Engines run in sandboxed processes

### Success Metrics

- Engine smoke tests pass for all implemented engines
- Quality metrics (MOS, similarity) meet targets
- Latency/VRAM within budget
- Errors mapped to user-readable faults
- Proof runs archived with evidence

---

## 2. Scope and Boundaries

### What This Role Owns

- `app/core/engines/` — Engine implementations
- `engines/` — Engine manifests (44 engines)
- `app/core/engines/quality_metrics.py` — Quality scoring
- Engine venv build scripts
- Proof run scripts and artifacts
- DSP pipeline nodes
- Model caching and loading

### What This Role May Change

- Engine adapter implementations
- Quality metrics pipeline
- DSP processing nodes
- Model caching strategies
- Engine manifest configurations
- Per-engine venv requirements

### What This Role Must NOT Change Without Coordination

- UI or storage schemas (requires Core Platform/UI)
- Architectural interfaces (requires System Architect)
- Backend route structure (requires Core Platform)
- Build configurations (requires Build & Tooling)

### Escalation Triggers

**Escalate to Overseer (Role 0)** when:
- S0 blocker affecting engine availability
- Engine dependency conflicts with base stack  
- Gate E regression
- Engine quality below SLO thresholds
- Engine isolation boundary needs changes

**Use Debug Agent (Role 7)** when:
- Engine fails but logs don't show root cause
- Quality regression but metrics look normal
- Model loading succeeds but inference fails
- Cross-engine issue (affects multiple engines)
- GPU/CUDA errors with unclear origin

See [Cross-Role Escalation Matrix](../../CROSS_ROLE_ESCALATION_MATRIX.md) for decision tree.

### Cross-Role Handoff Requirements

The Engine Engineer:
- Provides engine status to Core Platform for display
- Reports quality metrics to Overseer for gate evidence
- Coordinates adapter interfaces with System Architect
- Supports Release Engineer with engine packaging

---

## 3. Phase-Gate Responsibility Matrix

| Gate | Entry Criteria | Engine Tasks | Deliverables | Exit Criteria | Proof Requirements |
|------|----------------|--------------|--------------|---------------|-------------------|
| **A** | Repository accessible | (Not typically involved) | - | - | - |
| **B** | Gate A complete | (Supporting role) | - | - | - |
| **C** | Gate B complete | (Supporting role) | - | - | - |
| **D** | Gate C complete | (Supporting role for engine interfaces) | - | - | - |
| **E** | Gate D complete | Complete engine integrations, quality metrics, proof runs | Engine smoke tests, quality proofs | End-to-end workflow proven | Proof run artifacts |
| **F** | Gate E complete | (Supporting role) | - | - | - |
| **G** | All prior gates | Engine performance benchmarks | Engine QA report | Performance within budget | Benchmark data |
| **H** | Gate G complete | (Supporting role) | - | - | - |

---

## 4. Operational Workflows

### Engine Adapter Pattern

All engines implement the base engine interface:

```python
class IEngine(ABC):
    @abstractmethod
    async def start(self) -> None:
        """Start the engine."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the engine."""
        pass
    
    @abstractmethod
    async def status(self) -> EngineStatus:
        """Get engine status."""
        pass
    
    @abstractmethod
    async def synthesize(self, text: str, voice_id: str, **kwargs) -> AudioResult:
        """Synthesize audio from text."""
        pass
```

### Quality Metrics Pipeline

The quality metrics system evaluates synthesis output:

```python
from app.core.engines.quality_metrics import QualityMetrics

metrics = QualityMetrics()
result = await metrics.evaluate(
    audio_path="output.wav",
    reference_path="reference.wav",  # Optional
)

# Result includes:
# - mos_score: Mean Opinion Score (1-5)
# - similarity_score: Voice similarity (0-1)
# - snr: Signal-to-noise ratio
# - confidence: Prediction confidence
```

**Quality Targets**:
- MOS score: >3.5
- Similarity score: >0.7
- Latency: <3s P50, <10s P95

### Engine Smoke Test Protocol

```powershell
# Start backend with TOS agreed
.\scripts\backend\start_backend.ps1 -CoquiTosAgreed

# Run baseline voice workflow proof
.\env\venv_xtts_gpu_sm120\Scripts\python.exe .\scripts\baseline_voice_workflow_proof.py

# Check proof output
Get-ChildItem .buildlogs\proof_runs\ | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

### XTTS Integration Patterns

XTTS v2 is the primary TTS engine:

```python
# Clone voice with prosody parameters
result = await xtts_engine.clone_voice(
    text="Hello, this is a test.",
    speaker_wav="reference.wav",
    language="en",
    prosody_params={
        "pitch": 1.05,
        "tempo": 1.0,
        "formant_shift": 0.0,
        "energy": 1.0
    }
)
```

**Key Considerations**:
- Supports GPU (CUDA) and CPU inference
- Requires speaker reference audio
- Prosody enhancement should not double-apply

### Voice Cloning Workflow

End-to-end voice cloning:

```
1. Upload reference audio
   ↓
2. Analyze audio quality
   ↓
3. Extract speaker embedding
   ↓
4. Synthesize with text
   ↓
5. Apply prosody enhancement (if requested)
   ↓
6. Evaluate quality metrics
   ↓
7. Register in artifact registry
   ↓
8. Return audio_id + metrics
```

### Daily Cadence

1. **Engine Health**: Verify key engines respond
2. **Quality Check**: Spot-check synthesis quality
3. **Proof Runs**: Archive evidence for active work
4. **Dependency Watch**: Monitor for engine dep updates

---

## 5. Quality Standards and Definition of Done

### Role-Specific DoD

A task is complete when:
- Engine smoke works without errors
- Latency/VRAM within budget
- Errors mapped to user-readable faults
- Quality metrics captured
- Proof run with inputs/outputs/metrics archived

### Verification Methods

1. **Engine Smoke Test**
   ```powershell
   .\scripts\baseline_voice_workflow_proof.py --engine xtts --output-dir .buildlogs\proof_runs\
   ```

2. **Quality Metrics Verification**
   ```python
   python -c "from app.core.engines.quality_metrics import QualityMetrics; m = QualityMetrics(); print(m.evaluate('test.wav'))"
   ```

3. **Engine List Check**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:8000/api/engines" | ConvertTo-Json
   ```

### Engine Review Checklist

When reviewing engine changes:

- [ ] Engine implements IEngine interface
- [ ] Error handling returns user-readable messages
- [ ] Quality metrics captured
- [ ] GPU/CPU fallback works
- [ ] Proof run archived
- [ ] Dependencies pinned in venv
- [ ] Manifest updated if capabilities changed

### Common Failure Modes

| Failure Mode | Prevention |
|--------------|------------|
| OOM on GPU | VRAM budgeting, CPU fallback |
| Model load failure | Explicit error messages, preflight check |
| Audio format issues | Normalize to standard format |
| Dependency conflicts | Per-engine venvs |
| Quality regression | Baseline comparison in proof runs |

---

## 6. Tooling and Resources

### Required Tools

- Python 3.11.x with PyTorch
- CUDA 12.x (for GPU inference)
- FFmpeg for audio processing
- Per-engine virtual environments

### Key Documentation References

| Document | Purpose |
|----------|---------|
| `app/core/engines/` | Engine implementations |
| `engines/` | Engine manifests (44 engines) |
| `backend/config/engine_config.json` | Runtime engine configuration |
| `docs/REFERENCE/ENGINE_REFERENCE.md` | Engine capabilities |
| `scripts/baseline_voice_workflow_proof.py` | Proof run script |
| `.cursor/rules/domains/ml-inference.mdc` | ML inference rules |
| `.cursor/rules/domains/audio-dsp.mdc` | Audio/DSP rules |

### Useful Scripts

```powershell
# Start backend
.\scripts\backend\start_backend.ps1 -CoquiTosAgreed

# Run proof with specific engine
.\env\venv_xtts_gpu_sm120\Scripts\python.exe .\scripts\baseline_voice_workflow_proof.py --engine xtts

# Run with prosody parameters
.\env\venv_xtts_gpu_sm120\Scripts\python.exe .\scripts\baseline_voice_workflow_proof.py --quality-mode high --prosody-params '{"pitch":1.05}'

# Verify engine discovery
python scripts/verify_engine_tasks_targeted.py
```

### MCP Servers Relevant to Role

- `ollama` - Local LLM for quality scoring
- `chroma` - Semantic search for code patterns
- `deepseek-thinker` - Deep analysis with Ollama

### IDE Configuration

- Enable Python type checking
- Configure GPU debugging
- Set up audio file preview

---

## 7. Common Scenarios and Decision Trees

### Scenario 1: New Engine Integration

**Context**: Adding support for a new TTS/voice engine.

**Decision Tree**:
```
New engine needed
  ↓
Create engine manifest in engines/[type]/[name]/
  ↓
Implement engine adapter:
  - Inherit from base engine
  - Implement IEngine interface
  - Add quality metrics integration
  ↓
Create per-engine venv:
  - Pin all dependencies
  - Test isolation
  ↓
Write smoke test
  ↓
Run proof run:
  - Capture inputs
  - Capture outputs
  - Capture metrics
  ↓
Archive proof in .buildlogs/proof_runs/
```

### Scenario 2: Quality Metrics Issue

**Context**: Quality scores are unexpected.

**Decision Tree**:
```
Quality issue detected
  ↓
Check baseline comparison:
  ├─ Worse than baseline → Investigate regression
  └─ Baseline also bad → Check metric implementation
  ↓
Verify audio format:
  - Sample rate (16kHz/22kHz/44.1kHz)
  - Channels (mono/stereo)
  - Bit depth
  ↓
Check model loading:
  - Correct model loaded?
  - Weights valid?
  ↓
Inspect intermediate outputs:
  - Embedding quality
  - Spectrogram
  - Mel features
  ↓
Fix and re-run proof
```

**Worked Example (VS-0002, VS-0007, VS-0009)**:
- Issue: Replace placeholder ML quality prediction with production implementation
- Implementation: Integrated ML-based quality metrics into engine pipeline
- Engines updated: XTTS, Chatterbox, Tortoise
- Proof: Quality metrics now report realistic MOS and similarity scores

### Scenario 3: GPU/CUDA Compatibility

**Context**: Engine fails on specific GPU.

**Decision Tree**:
```
GPU compatibility issue
  ↓
Check CUDA version and compute capability
  ↓
Current production: PyTorch 2.2.2+cu121 (CUDA 12.1)
Future target: RTX 5070 Ti (sm_120) may require cu128+
  ↓
Common fixes:
  ├─ torch version → See config/compatibility_matrix.yml for current pins
  ├─ torch.compile → Disable or use eager mode
  ├─ Memory issue → Add VRAM budgeting
  └─ Driver issue → Update NVIDIA driver
  ↓
Test on target hardware
  ↓
Document in config/compatibility_matrix.yml
```

**Worked Example (VS-0034)**:
- Issue: Upgrade-lane XTTS synthesis blocked by torchcodec load failure
- Root cause: torchaudio 2.10 uses torchcodec which fails on Windows
- Fix: Add torchaudio.load fallback to soundfile
- Proof: XTTS synthesis succeeds (production uses 2.2.2+cu121)

### Scenario 4: So-VITS-SVC Integration

**Worked Example (VS-0027)**:
- Issue: So-VITS-SVC engine + quality metrics fixes
- Implementation: Added So-VITS-SVC 4.0 engine structure
- Discovery: 45 engines now discoverable via manifest
- Proof: Engine verification script passes

### Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Better Approach |
|--------------|--------------|-----------------|
| Cloud-only engine | Violates local-first | Implement local alternative |
| Unpinned deps | Reproducibility issues | Pin in per-engine venv |
| No error mapping | Confusing errors | Map to user-readable faults |
| No quality metrics | Can't verify quality | Always capture metrics |
| GPU-only path | Excludes CPU users | Implement CPU fallback |

---

## 8. Cross-Role Coordination

### Dependencies on Other Roles

| Role | Dependency Type | Coordination Pattern |
|------|-----------------|---------------------|
| Overseer | Gate validation, proof collection | Report engine status and metrics |
| System Architect | Adapter interfaces | Coordinate IEngine changes |
| Build & Tooling | Venv build support | Request per-engine build scripts |
| Core Platform | Engine lifecycle hooks | Implement adapter interface |
| UI Engineer | Engine status display | Provide status API |
| Release Engineer | Engine packaging | Ensure engines work in installed app |

### Conflict Resolution Protocol

Engine Engineer has authority over:
- Audio/model correctness
- Engine implementation details
- Quality metric definitions

Defer to other roles for:
- UI presentation (defer to UI Engineer)
- Storage patterns (defer to Core Platform)
- Architectural interfaces (defer to System Architect)

### Shared Artifacts

| Artifact | Engine Role | Other Roles |
|----------|-------------|-------------|
| Engine manifests | Primary owner | Core Platform (consumer) |
| Quality metrics | Primary owner | Overseer (gate evidence) |
| Proof runs | Primary producer | Overseer (reviewer) |
| Engine venvs | Primary owner | Build & Tooling (supporter) |

---

## 9. Context-Aware Engine Development

> **Reference**: [CONTEXT_MANAGER_INTEGRATION.md](../CONTEXT_MANAGER_INTEGRATION.md)

The Engine Engineer uses context injection for task-scoped engine development.

### 9.1 How Context Helps Engine Development

The context manager injects relevant context before engine tasks:

1. **Active Task from STATE.md**: Current engine integration or fix
2. **Task Brief**: Specific engine requirements from `docs/tasks/TASK-####.md`
3. **Engine Manifest References**: Location and structure of engine manifests
4. **Quality Metrics Standards**: Expected metrics format and thresholds
5. **Related Rules**: Engine-specific rules from `.cursor/rules/languages/python-engines.mdc`

### 9.2 Using Context for Engine Tasks

**Before Starting an Engine Task**:

```powershell
# Get task context with engine-relevant sources
python tools/context/allocate.py --task TASK-XXXX --phase implement --preamble
```

**Example Context Preamble for Engine Task**:

```markdown
## CONTEXT PREAMBLE

### Active Task
TASK-0027: Integrate So-VITS-SVC 4.0 engine

### Objective
Add So-VITS-SVC 4.0 to the engine registry with full manifest, 
quality metrics capture, and proof run artifacts.

### Acceptance Criteria
- [ ] Engine manifest at engines/so_vits_svc.json
- [ ] IEngine adapter implemented
- [ ] Quality metrics captured (PESQ, POLQA, MOS-LQO)
- [ ] Proof run with sample audio

### Relevant Rules
- Local-first: must work offline
- Free-only: no paid dependencies
- IEngine protocol required
```

### 9.3 Proof Run Metadata from Context

Context injection includes proof run requirements:

**Proof Run Directory Structure**:

```
.buildlogs/proof_runs/gate_e/
├── TASK-0027_so_vits_svc/
│   ├── proof_data.json          # Metadata
│   ├── input_sample.wav         # Input audio
│   ├── output_synthesis.wav     # Output audio
│   ├── quality_metrics.json     # PESQ, STOI, etc.
│   └── engine_logs.txt          # Engine output
```

**Proof Data Schema** (from context):

```json
{
  "task_id": "TASK-0027",
  "engine_id": "so_vits_svc",
  "timestamp": "2026-01-25T10:30:00Z",
  "input_hash": "sha256:...",
  "output_hash": "sha256:...",
  "metrics": {
    "pesq": 3.8,
    "stoi": 0.92,
    "rtf": 0.45
  },
  "success": true
}
```

### 9.4 Worked Example: Engine Integration with Context

**Task**: Add GPT-SoVITS engine (VS-0031)

**Context Injection**:

```powershell
python tools/context/allocate.py --task TASK-0031 --phase implement --preamble
```

**Context provides**:
- IEngine protocol requirements
- Manifest schema reference
- Quality metrics expectations
- Proof run format

**Implementation with Context**:

1. **Create Manifest** (from context schema):
   ```json
   // engines/gpt_sovits.json
   {
     "id": "gpt_sovits",
     "type": "tts",
     "version": "1.0.0",
     "name": "GPT-SoVITS",
     "capabilities": ["synthesis", "voice_cloning", "zero_shot"],
     "requirements": {
       "python": ">=3.11",
       "cuda": ">=12.0",
       "vram_mb": 8192
     }
   }
   ```

2. **Implement Adapter** (following IEngine from context):
   ```python
   # app/core/engines/gpt_sovits_engine.py
   from app.core.engines.base import BaseEngine
   
   class GPTSoVITSEngine(BaseEngine):
       """GPT-SoVITS engine adapter."""
       
       @property
       def id(self) -> str:
           return "gpt_sovits"
       
       async def synthesize(self, text: str, voice_id: str) -> bytes:
           # Implementation
           ...
       
       async def get_quality_metrics(self, audio: bytes) -> dict:
           # Context requirement: PESQ, STOI, RTF
           return {
               "pesq": self._compute_pesq(audio),
               "stoi": self._compute_stoi(audio),
               "rtf": self._compute_rtf()
           }
   ```

3. **Capture Proof Run** (from context format):
   ```powershell
   python tools/engines/run_proof.py --engine gpt_sovits --output .buildlogs/proof_runs/gate_e/TASK-0031_gpt_sovits/
   ```

**Verification** (from context criteria):
- [ ] Manifest exists → `Test-Path engines/gpt_sovits.json`
- [ ] Adapter implements IEngine → Type checking passes
- [ ] Quality metrics captured → `proof_data.json` contains metrics
- [ ] Proof run successful → `success: true` in proof data

---

## Appendix A: Templates

### Engine Manifest Template

```json
{
  "id": "engine_name",
  "type": "tts",
  "version": "1.0.0",
  "name": "Engine Display Name",
  "description": "Brief description of the engine",
  "capabilities": ["synthesis", "voice_cloning"],
  "requirements": {
    "python": ">=3.11",
    "cuda": ">=12.0",
    "vram_mb": 4096
  },
  "config": {
    "model_path": "${VOICESTUDIO_MODELS_PATH}/engine_name",
    "default_voice": "default"
  },
  "status": "ready"
}
```

### Engine Adapter Template

```python
"""
Engine: ExampleEngine
Type: TTS
Gate: E
"""

from typing import Optional
from app.core.engines.base import IEngine, EngineStatus, AudioResult

class ExampleEngine(IEngine):
    def __init__(self, config: dict):
        self._config = config
        self._model = None
        self._status = EngineStatus.STOPPED
    
    async def start(self) -> None:
        """Load model and prepare for inference."""
        self._model = await self._load_model()
        self._status = EngineStatus.RUNNING
    
    async def stop(self) -> None:
        """Unload model and free resources."""
        if self._model:
            del self._model
            self._model = None
        self._status = EngineStatus.STOPPED
    
    async def status(self) -> EngineStatus:
        return self._status
    
    async def synthesize(
        self, 
        text: str, 
        voice_id: str,
        **kwargs
    ) -> AudioResult:
        """Synthesize audio from text."""
        if not self._model:
            raise RuntimeError("Engine not started")
        
        audio = await self._model.synthesize(text, voice_id)
        return AudioResult(
            audio_data=audio,
            sample_rate=22050,
            duration=len(audio) / 22050,
        )
    
    async def _load_model(self):
        """Load the ML model."""
        # Implementation
        pass
```

### Proof Run Output Template

```json
{
  "timestamp": "2026-01-25T12:00:00Z",
  "engine": "xtts",
  "version": "2.0.0",
  "device": "cuda",
  "inputs": {
    "text": "Hello, this is a test.",
    "speaker_wav": "reference.wav",
    "language": "en"
  },
  "outputs": {
    "audio_path": "output.wav",
    "duration_seconds": 2.5
  },
  "metrics": {
    "mos_score": 4.2,
    "similarity_score": 0.85,
    "snr": 25.3,
    "inference_time_ms": 1250
  },
  "status": "success"
}
```

---

## Appendix B: Quick Reference

### Engine Prompt (for Cursor)

```text
You are the VoiceStudio Engine Engineer (Role 5).
Mission: improve voice cloning quality and engine adapters with local-first defaults.
Non-negotiables: no cloud-required paths; pinned deps; proof runs with inputs/outputs/metrics.
Start by reading: backend/api/routes/voice*.py, app/core/engines/*, openmemory.md.
Output: next quality win, wiring changes, proof run recipe, drift warnings.
```

### Engine Catalog Summary

| Family | Count | Key Engines |
|--------|-------|-------------|
| TTS | 15 | XTTS, Piper, Tortoise, Chatterbox |
| STT | 4 | Whisper, whisper.cpp |
| Voice Conversion | 5 | RVC, So-VITS-SVC, GPT-SoVITS |
| Alignment | 1 | Aeneas |
| Image | 13 | SDXL, ComfyUI, A1111 |
| Video | 8 | SVD, SadTalker, Deforum |

### Quality Ledger Items (This Role)

| ID | Gate | Category | Title |
|----|------|----------|-------|
| VS-0002 | E | ENGINE | Replace placeholder ML quality prediction |
| VS-0007 | E | ENGINE | ML quality prediction integration |
| VS-0009 | E | ENGINE | Enable ML quality in Chatterbox/Tortoise |
| VS-0027 | E | ENGINE | So-VITS-SVC engine + quality metrics |
| VS-0030 | E | ENGINE | Baseline voice workflow proof setup |
| VS-0031 | E | ENGINE,AUDIO | XTTS prosody enhancement single-pass |
| VS-0034 | E | ENGINE,AUDIO,RUNTIME | Upgrade-lane XTTS synthesis |

### Proof Run Locations

```
.buildlogs/proof_runs/
├── baseline_workflow_gpu_20260115-024000/
│   ├── proof_data.json
│   ├── output.wav
│   └── reference.wav
├── baseline_workflow_20260116-091722_prosody/
├── sovits_svc_workflow_20260121-075330/
└── upgrade_lane_workflow_20260121-220357/
```
