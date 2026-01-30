# VS-0030: Baseline Voice Workflow Proof Setup

**State:** DONE (proof captured)  
**Severity:** S2 Major  
**Gate:** E  
**Owner role:** Engine Engineer  
**Reviewer role:** Release Engineer  
**Categories:** ENGINE  
**Introduced:** 2026-01-13  
**Last verified:** 2026-01-14 (Windows 10.0.26200)

## Summary

Created baseline end-to-end voice workflow proof script to establish quality baseline for future improvements. The script runs:
1. XTTS v2 synthesis
2. whisper.cpp transcription  
3. Quality metrics capture

All evidence (inputs, outputs, metrics, model paths) is captured for baseline comparison.

## Change Set

### Files Created

- `scripts/baseline_voice_workflow_proof.py` - Main proof script
- `scripts/README_BASELINE_PROOF.md` - Usage documentation
- `docs/governance/overseer/handoffs/VS-0030_BASELINE_PROOF_SETUP.md` - This handoff document

### Script Features

- **Backend health check**: Verifies API accessibility before running
- **Profile management**: Automatically uses existing profiles or creates minimal test profile
- **Evidence capture**: Saves all inputs, outputs, metrics, and configuration to timestamped directory
- **Error handling**: Graceful failure with clear error messages
- **Quality metrics**: Captures complete quality metrics from synthesis (MOS, similarity, naturalness, SNR, etc.)
- **Model path tracking**: Captures model paths and configuration from backend

## Proof Run (Required)

The proof script is ready but requires the backend API to be running. To execute:

### Step 1: Start Backend API

```powershell
# From project root
.\start_backend.ps1

# Or manually:
uvicorn backend.api.main:app --port 8001
```

### Step 2: Run Baseline Proof

```powershell
# From project root
python scripts/baseline_voice_workflow_proof.py
```

### Step 3: Review Output

The script creates a timestamped directory under `proof_runs/` containing:
- `proof_data.json` - Complete proof data (inputs, outputs, metrics, config)
- `{audio_id}.wav` - Synthesized audio file (if available)

### Proof run (PASS — captured)

- **Backend**: `.\start_backend.ps1 -CoquiTosAgreed` (ensures XTTS CPML prompt is non-interactive)
- **Proof**: `.\venv\Scripts\python.exe .\scripts\baseline_voice_workflow_proof.py`
- **Result**: ✅ PASS (XTTS synth → whisper.cpp transcribe → metrics captured)
- **Evidence directory**: `proof_runs\baseline_workflow_20260114-052929\`
  - `proof_data.json`
  - `clone_clone_bafc0ecadb3d_046b48bf.wav`
  - `test_reference.wav`

Key metrics snapshot (from `proof_data.json`):
- `mos_score`: 4.7777
- `similarity`: 0.8240
- `naturalness`: 1.0000
- `snr_db`: 82.5928

### Expected Output Structure

```json
{
  "timestamp": "2026-01-13T15:30:45.123456",
  "workflow": "baseline_voice_workflow",
  "steps": [
    {
      "step": "synthesize",
      "status": "success",
      "audio_id": "synth_abc123",
      "duration_seconds": 2.45,
      "quality_metrics": {
        "mos_score": 4.2,
        "similarity": 0.87,
        "naturalness": 0.82,
        "snr_db": 28.5,
        "artifacts_detected": false
      }
    },
    {
      "step": "transcribe",
      "status": "success",
      "text": "...",
      "language": "en",
      "segments_count": 3
    }
  ],
  "inputs": {
    "text": "Hello, this is a baseline voice workflow proof...",
    "language": "en",
    "synthesis": {
      "engine": "xtts_v2",
      "text": "...",
      "language": "en"
    },
    "transcription": {
      "audio_id": "synth_abc123",
      "engine": "whisper_cpp",
      "word_timestamps": true
    }
  },
  "outputs": {
    "synthesis": {
      "audio_id": "synth_abc123",
      "audio_url": "/api/voice/audio/synth_abc123",
      "duration": 2.45
    },
    "transcription": {
      "text": "...",
      "language": "en",
      "segments": [...]
    },
    "audio_file_path": "E:\\VoiceStudio\\proof_runs\\...\\synth_abc123.wav"
  },
  "metrics": {
    "synthesis": {
      "mos_score": 4.2,
      "similarity": 0.87,
      "naturalness": 0.82,
      "snr_db": 28.5
    }
  },
  "config": {
    "engine": "xtts_v2",
    "language": "en",
    "profile_id": "profile_123",
    "profile_source": "existing",
    "model_paths": {
      "xtts": "E:\\VoiceStudio\\models\\tts_models\\multilingual\\multi-dataset\\xtts_v2",
      "whisper_cpp": "E:\\VoiceStudio\\models\\whisper\\whisper-medium.en.gguf"
    }
  }
}
```

## Implementation Details

### Script Architecture

- **BaselineWorkflowProof class**: Main orchestrator
- **Health check**: Verifies backend accessibility before execution
- **Profile management**: Handles profile creation/retrieval automatically
- **Evidence capture**: Comprehensive data collection for baseline comparison
- **Error handling**: Graceful failures with detailed error messages

### Quality Metrics Captured

- **MOS Score**: Mean Opinion Score (1.0-5.0)
- **Similarity**: Voice similarity to reference (0.0-1.0)
- **Naturalness**: Naturalness score (0.0-1.0)
- **SNR**: Signal-to-noise ratio (dB)
- **Artifacts**: Artifact detection results
- **Additional metrics**: Any other metrics returned by the quality system

### Model Path Tracking

The script captures:
- XTTS v2 model path
- whisper.cpp model path
- Any other model paths from backend preflight

## Next Steps

1. **Execute proof**: Run the script when backend is available (see Proof Run section above)
2. **Review baseline**: Analyze `proof_data.json` for quality metrics baseline
3. **Document baseline**: Record baseline metrics in quality upgrade ledger
4. **Plan improvements**: Use baseline to identify quality improvement opportunities
5. **Track upgrades**: Each quality upgrade should be compared against this baseline

## Command Reference

### Basic Usage

```bash
python scripts/baseline_voice_workflow_proof.py
```

### With Custom Options

```bash
python scripts/baseline_voice_workflow_proof.py \
    --backend-url http://localhost:8001 \
    --text "Your custom test text" \
    --language en \
    --profile-id profile_123
```

### View Help

```bash
python scripts/baseline_voice_workflow_proof.py --help
```

## Troubleshooting

### Backend Not Running

**Error**: `Backend API is not accessible`

**Solution**: Start backend server:
```powershell
.\start_backend.ps1
```

### No Profiles Available

**Warning**: `No existing profiles found`

**Solution**: Script will attempt to create a minimal profile. For best results, create a profile with reference audio first.

### Synthesis Fails

**Check**:
1. XTTS v2 model is available (check `E:\VoiceStudio\models`)
2. Voice profile exists (if required)
3. Backend logs for detailed errors

### Transcription Fails

**Check**:
1. whisper.cpp model is available
2. Audio file was successfully synthesized
3. Backend logs for detailed errors

## Links

- Script: `scripts/baseline_voice_workflow_proof.py`
- Documentation: `scripts/README_BASELINE_PROOF.md`
- Engine Engineer tasks: `docs/governance/overseer/role_tasks/ENGINE_ENGINEER.md`
- Quality metrics: `app/core/engines/quality_metrics.py`

## Related Entries

- VS-0027: So-VITS-SVC engine + quality metrics fixes (baseline quality metrics system)
- VS-0002: ML quality prediction implementation (quality metrics foundation)
- VS-0007: ML quality prediction integration (quality metrics integration)
