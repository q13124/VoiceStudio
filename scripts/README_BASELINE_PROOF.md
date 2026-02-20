# Baseline Voice Workflow Proof

## Purpose

This script runs a baseline end-to-end voice workflow proof to establish a quality baseline for future improvements. The workflow consists of:

1. **XTTS v2 Synthesis**: Synthesize speech from text using XTTS v2 engine
2. **whisper.cpp Transcription**: Transcribe the synthesized audio using whisper.cpp
3. **Quality Metrics Capture**: Capture all quality metrics from synthesis

## Prerequisites

1. **Backend API Running**: The VoiceStudio backend API must be running

   ```powershell
   # Start backend (from project root)
   .\scripts/backend/start_backend.ps1
   # Or manually:
   uvicorn backend.api.main:app --port 8000
   ```

   If port `8000` is already in use, `scripts/backend/start_backend.ps1` will switch to an
   alternate port (8002/8080/8888). The proof script will auto-detect the
   backend when using the default URL, but you can always pass `--backend-url`
   to pin the exact port.

2. **Required Models**:

   - XTTS v2 model (auto-downloaded to `E:\VoiceStudio\models` if not present)
   - whisper.cpp model (auto-downloaded if not present)

3. **Voice Profile** (optional but recommended):
   - The script will attempt to use an existing profile or create a minimal one
   - For best results, create a profile with reference audio first:
     ```bash
     # Create profile via API or UI
     POST /api/profiles
     ```

## Usage

### Basic Usage

```bash
python scripts/baseline_voice_workflow_proof.py
```

### GPU Lane (sm_120)

Use the GPU venv and backend launcher, then run the proof with an output folder under `.buildlogs\proof_runs\`.

```powershell
.\scripts/backend/start_backend.ps1 -Gpu -CoquiTosAgreed
```

```powershell
.\env\venv_xtts_gpu_sm120\Scripts\python.exe .\scripts\baseline_voice_workflow_proof.py `
  --output-dir E:\VoiceStudio\.buildlogs\proof_runs\baseline_workflow_gpu_run
```

The proof artifact records the device used in `proof_data.json` (`steps[].device` and `config.device`).

### Multi-Reference + Prosody

Pass multiple `--reference-audio` entries and enable `--use-multi-reference`. Prosody controls use
`--prosody-params` with a JSON object.

```powershell
.\env\venv_xtts_gpu_sm120\Scripts\python.exe .\scripts\baseline_voice_workflow_proof.py `
  --reference-audio E:\VoiceStudio\.buildlogs\proof_runs\baseline_workflow_gpu_run\ref_a.wav `
  --reference-audio E:\VoiceStudio\.buildlogs\proof_runs\baseline_workflow_gpu_run\ref_b.wav `
  --use-multi-reference `
  --prosody-params "{\"pitch\":1.0,\"tempo\":1.0,\"formant_shift\":1.0,\"energy\":1.0}"
```

Multi-reference runs store side-by-side candidate metrics in `proof_data.json` under
`steps[].candidate_metrics`.

### So-VITS-SVC Conversion Proof

Once a So-VITS-SVC checkpoint + config exist under `E:\VoiceStudio\models\checkpoints\`, run:

Run the proof with the `--checkpoint-path` and `--config-path` flags pointing to the So-VITS-SVC checkpoint `.pth` and config `.json` files.

The script records conversion output, device, and metrics under a new `.buildlogs\proof_runs\` folder.

So-VITS-SVC conversion requires an external inference command. Configure one of the following:

- `SOVITS_SVC_INFER_COMMAND` environment variable, or
- `infer_command` in `backend/config/engine_config.json` for the `sovits_svc` engine.

The command template must accept `{input}`, `{output}`, `{checkpoint}`, `{config}`, `{pitch_shift}`, `{device}`, and `{sample_rate}`. Without it (and without `allow_passthrough`), `/api/rvc/convert` returns HTTP 424.

### With Custom Options

```bash
python scripts/baseline_voice_workflow_proof.py \
    --backend-url http://localhost:8000 \
    --text "Your custom test text here" \
    --language en \
    --profile-id profile_123
```

### Command-Line Arguments

- `--backend-url`: Backend API URL (default: `http://localhost:8000`)
- `--text`: Text to synthesize (default: baseline test text)
- `--language`: Language code (default: `en`)
- `--profile-id`: Voice profile ID (optional, will try to get/create one)
- `--output-dir`: Output directory for proof artifacts (default: timestamped directory)

## Output

The script creates a timestamped directory under `.buildlogs\proof_runs\` containing:

- **`proof_data.json`**: Complete proof data including:

  - Inputs (text, language, engine config)
  - Outputs (audio_id, audio_url, transcription text)
  - Quality metrics (MOS, similarity, naturalness, SNR, etc.)
  - Model paths and configuration
  - Dependency versions (python/torch/torchaudio/transformers)
  - Step-by-step execution results

- **`{audio_id}.wav`**: Downloaded synthesized audio file (if available)

## Example Output

```
2026-01-13 15:30:45 - __main__ - INFO - Backend API is accessible
2026-01-13 15:30:45 - __main__ - INFO - Step 1: Synthesizing with XTTS v2...
2026-01-13 15:31:12 - __main__ - INFO - Synthesis complete: audio_id=synth_abc123, duration=2.45s
2026-01-13 15:31:12 - __main__ - INFO - Quality metrics: {
  "mos_score": 4.2,
  "similarity": 0.87,
  "naturalness": 0.82,
  "snr_db": 28.5
}
2026-01-13 15:31:12 - __main__ - INFO - Step 2: Transcribing with whisper_cpp...
2026-01-13 15:31:18 - __main__ - INFO - Transcription complete: language=en
2026-01-13 15:31:18 - __main__ - INFO - ✅ Baseline proof completed successfully
```

## Proof Data Structure

The `proof_data.json` file contains:

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
      "quality_metrics": { ... }
    },
    {
      "step": "transcribe",
      "status": "success",
      "text": "...",
      "language": "en"
    }
  ],
  "inputs": {
    "text": "...",
    "language": "en",
    "synthesis": { ... },
    "transcription": { ... }
  },
  "outputs": {
    "synthesis": { ... },
    "transcription": { ... },
    "audio_file_path": "..."
  },
  "metrics": {
    "synthesis": { ... }
  },
  "config": {
    "engine": "xtts_v2",
    "language": "en",
    "profile_id": "...",
    "model_paths": { ... },
    "dependency_versions": {
      "python": "...",
      "python_executable": "...",
      "torch": "...",
      "torchaudio": "...",
      "transformers": "..."
    }
  }
}
```

## Troubleshooting

### Backend Not Accessible

```
ERROR: Backend API is not accessible. Please start the backend server.
```

**Solution**: Start the backend server:

```powershell
.\scripts/backend/start_backend.ps1
```

### /api/voice/clone returns 404

If the backend started on an alternate port, the default proof URL (`8000`)
may point at an older process with missing voice routes.

**Solution**: Re-run the proof with the port printed by `scripts/backend/start_backend.ps1`:

```powershell
.\env\venv_xtts_gpu_sm120\Scripts\python.exe .\scripts\baseline_voice_workflow_proof.py `
  --backend-url http://localhost:8080
```

### xtts_v2 not available

If the proof reports that `xtts_v2` is not available, the backend was started
without the XTTS engine deps.

**Solution**: Install the XTTS profile and restart the backend using that venv:

```powershell
.\scripts\install-engine-deps.ps1 -Profile xtts
.\scripts/backend/start_backend.ps1 -CoquiTosAgreed
```

### No Profiles Available

```
WARNING: No existing profiles found. Profile creation requires reference audio.
```

**Solution**: The script will attempt to create a minimal profile. For best results, create a profile with reference audio via the API or UI first.

### Synthesis Fails

If synthesis fails, check:

1. XTTS v2 model is available (check `E:\VoiceStudio\models`)
2. Voice profile exists and has reference audio (if required)
3. Backend logs for detailed error messages

### Transcription Fails

If transcription fails, check:

1. whisper.cpp model is available
2. Audio file was successfully synthesized
3. Backend logs for detailed error messages

## Next Steps

After running the baseline proof:

1. Review `proof_data.json` for quality metrics baseline
2. Use this baseline to compare future quality improvements
3. Document any issues or missing dependencies
4. Create ledger entry for quality upgrade work items

## Related Documentation

- Engine Engineer tasks: `docs/governance/overseer/role_tasks/ENGINE_ENGINEER.md`
- Quality metrics: `app/core/engines/quality_metrics.py`
- API documentation: `docs/api/ENDPOINTS.md`
