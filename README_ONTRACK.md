
# VoiceStudio — ON‑TRACK NOW Skeleton
Generated: 2025-10-21T12:58:23.484631Z

This package wires the **Overseer + Agents/Workers** baseline so your 15‑minute `[OVERSEER]` loop has real data to emit and the architecture matches your governance.

## What’s inside
- `core/api/protocols/agents.py` — Agent protocol (start/report/enqueue).
- `core/api/protocols/workers.py` — Worker protocol (process/health).
- `workers/orchestrator.py` — Minimal orchestrator wiring agents/workers.
- `workers/agents/*` — Five agents (quality, performance, training, data, A/B) stubs.
- `workers/*_worker.py` — generation/processing/training worker stubs.
- `services/telemetry/*` — lightweight metrics + JSONL event log.
- `services/overseer/emit_report.py` — turns telemetry into an Overseer report dict.
- `config/overseer_config.yaml` — minimal stub (replace with your full YAML if desired).
- `tools/OVERSEER_Run.ps1` — one‑shot wrapper to print a digest.

## Quick start
```powershell
# From repo root after unpacking...
pwsh -ExecutionPolicy Bypass -File .\tools\OVERSEER_Run.ps1

# (Optional) smoke test the orchestrator
python -m workers.orchestrator --once
```
The runner will tell you if `config\overseer_config.yaml` is in the **right place**.

## Next steps
1. Point your 15‑minute automation to `config/overseer_config.yaml`.
2. If you want blocking guardrails, set `escalation.tier: 3` in that YAML.
3. Wire the emit_report output into your notifier to render the in‑app card.
