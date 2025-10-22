UltraClone — API + Schemas + Mastering Stubs
============================================

This bundle includes:
- openapi.yaml — HTTP contract for voices, TTS, batch, and quality report
- /schemas/*.json — JSON Schemas for VoiceProfile, VoicePreset, BatchJob, QualityReport
- /pipelines/mastering_pipeline.py — mastering chain stubs (order enforced)
- /tests/test_mastering_pipeline.py — smoke test for symbols

How to use
----------
1) Point your server generator (FastAPI or similar) at openapi.yaml for route scaffolding.
2) Validate your data models with the JSON Schemas (or mirror them into Pydantic models).
3) Fill in the mastering stubs with real DSP (pyloudnorm, numpy/scipy, etc.).
4) Keep the order: denoise -> EQ -> compress -> loudness(-16 LUFS) -> de-ess -> limit(-1 dBFS).

File paths
----------
Bundle root: UltraClone_Spec_Bundle
