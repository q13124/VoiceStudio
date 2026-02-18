# {{DISPLAY_NAME}} Audio Effect Processor Template

Production-oriented backend plugin template for audio effect processors.

## Includes

- `ProcessorPlugin`-style processing contract implementation
- FastAPI route adapter (`/process`, `/health`)
- Typed parameter validation (`parameters.py`)
- Isolated DSP logic (`processor.py`)
- DSP helper utilities (`dsp_utils.py`)
- Preset files (`presets/default.json`, `presets/voice.json`)
- Unit, contract, and micro-benchmark tests
- Fixture generation script for reproducible WAV assets

## Quick Start

1. Replace template tokens:
   - `{{PLUGIN_NAME}}`
   - `{{CLASS_NAME}}`
   - `{{DISPLAY_NAME}}`
   - `{{VERSION}}`
   - `{{AUTHOR}}`
   - `{{DESCRIPTION}}`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run tests:
   - `python -m pytest tests -v`

## Contract Notes

- Processing interface accepts float32 PCM samples.
- Internal processing path converts to/from bytes to satisfy processor plugin
  contracts.
- Keep DSP in `processor.py` and keep route/lifecycle glue in `plugin.py`.
