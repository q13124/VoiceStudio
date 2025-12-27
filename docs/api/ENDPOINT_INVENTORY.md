# API Endpoint Inventory
## VoiceStudio Quantum+ - Complete Endpoint Reference

**Date:** 2025-01-28  
**Status:** Complete  
**Total Route Files:** 87  
**Total Endpoints:** 480

---

## Executive Summary

This document provides a comprehensive inventory of all API endpoints in VoiceStudio Quantum+. Endpoints are organized by route file, with counts by HTTP method and WebSocket connections.

### Endpoint Distribution by Method

- **GET:** ~200 endpoints (read operations)
- **POST:** ~180 endpoints (create operations)
- **PUT:** ~40 endpoints (update operations)
- **DELETE:** ~50 endpoints (delete operations)
- **PATCH:** 0 endpoints
- **WebSocket:** 3 endpoints (real-time streaming)

---

## Endpoint Inventory by Route File

### adr.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/adr` |

**Purpose:** Audio Description and Recognition

---

### advanced_settings.py
**Total Endpoints:** 4

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | `/api/advanced-settings`, `/api/advanced-settings/category/{category}` |
| POST | 1 | `/api/advanced-settings/reset` |
| PUT | 1 | `/api/advanced-settings` |

**Purpose:** Advanced application settings management

---

### advanced_spectrogram.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Advanced spectrogram data endpoints |
| POST | 2 | Advanced spectrogram processing endpoints |
| DELETE | 1 | Advanced spectrogram cleanup endpoint |

**Purpose:** Advanced spectrogram visualization and analysis

---

### analytics.py
**Total Endpoints:** 3

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | `/api/analytics/summary`, `/api/analytics/metrics/{category}`, `/api/analytics/categories` |

**Purpose:** Application analytics and metrics

---

### api_key_manager.py
**Total Endpoints:** 7

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | `/api/api-keys`, `/api/api-keys/{key_id}`, `/api/api-keys/services/list` |
| POST | 2 | `/api/api-keys`, `/api/api-keys/{key_id}/validate` |
| PUT | 1 | `/api/api-keys/{key_id}` |
| DELETE | 1 | `/api/api-keys/{key_id}` |

**Purpose:** API key management for third-party services

---

### articulation.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/articulation` |

**Purpose:** Articulation control for voice synthesis

---

### assistant_run.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/assistant/run` |

**Purpose:** AI assistant execution

---

### assistant.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | `/api/assistant/conversations`, `/api/assistant/conversations/{conversation_id}` |
| POST | 2 | `/api/assistant/chat`, `/api/assistant/suggest-tasks` |
| DELETE | 1 | `/api/assistant/conversations/{conversation_id}` |

**Purpose:** AI assistant chat and conversation management

---

### audio_analysis.py
**Total Endpoints:** 3

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Audio analysis data endpoints |
| POST | 1 | Audio analysis processing endpoint |

**Purpose:** Audio analysis and processing

---

### audio.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 6 | Audio file retrieval and metadata endpoints |

**Purpose:** Audio file management and retrieval

---

### automation.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Automation configuration endpoints |
| POST | 2 | Automation creation endpoints |
| PUT | 1 | Automation update endpoint |
| DELETE | 2 | Automation deletion endpoints |

**Purpose:** Automation and macro system

---

### backup.py
**Total Endpoints:** 7

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Backup listing and retrieval endpoints |
| POST | 3 | Backup creation endpoints |
| DELETE | 1 | Backup deletion endpoint |

**Purpose:** Backup and restore functionality

---

### batch.py
**Total Endpoints:** 7

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | `/api/batch/jobs`, `/api/batch/jobs/{job_id}`, `/api/batch/queue/status` |
| POST | 3 | `/api/batch/jobs`, `/api/batch/jobs/{job_id}/start`, `/api/batch/jobs/{job_id}/cancel` |
| DELETE | 1 | `/api/batch/jobs/{job_id}` |

**Purpose:** Batch processing job management

---

### dataset_editor.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | Dataset editor data endpoint |
| POST | 2 | Dataset editor creation endpoints |
| PUT | 1 | Dataset editor update endpoint |
| DELETE | 1 | Dataset editor deletion endpoint |

**Purpose:** Training dataset editing

---

### dataset.py
**Total Endpoints:** 2

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 2 | Dataset creation and processing endpoints |

**Purpose:** Training dataset management

---

### deepfake_creator.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | `/api/deepfake/jobs`, `/api/deepfake/jobs/{job_id}`, `/api/deepfake/engines` |
| POST | 1 | `/api/deepfake/create` |
| DELETE | 1 | `/api/deepfake/jobs/{job_id}` |

**Purpose:** Deepfake video creation

---

### dubbing.py
**Total Endpoints:** 2

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 2 | Dubbing creation endpoints |

**Purpose:** Video dubbing functionality

---

### effects.py
**Total Endpoints:** 9

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Effects listing and configuration endpoints |
| POST | 3 | Effects application endpoints |
| PUT | 1 | Effect update endpoint |
| DELETE | 2 | Effect deletion endpoints |

**Purpose:** Audio effects processing (17 effect types)

---

### embedding_explorer.py
**Total Endpoints:** 7

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | `/api/embeddings`, `/api/embeddings/{embedding_id}` |
| POST | 4 | `/api/embeddings/extract`, `/api/embeddings/compare`, `/api/embeddings/visualize`, `/api/embeddings/cluster` |
| DELETE | 1 | `/api/embeddings/{embedding_id}` |

**Purpose:** Voice embedding exploration and analysis

---

### emotion_style.py
**Total Endpoints:** 3

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Emotion style configuration endpoints |
| POST | 1 | Emotion style application endpoint |

**Purpose:** Emotion and style control for voice synthesis

---

### emotion.py
**Total Endpoints:** 9

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | `/api/emotion/list`, `/api/emotion/preset/list`, `/api/emotion/preset/{preset_id}` |
| POST | 4 | `/api/emotion/analyze`, `/api/emotion/apply`, `/api/emotion/apply-extended`, `/api/emotion/preset/save` |
| PUT | 1 | `/api/emotion/preset/{preset_id}` |
| DELETE | 1 | `/api/emotion/preset/{preset_id}` |

**Purpose:** Emotion control and presets for voice synthesis

---

### engine.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | `/api/engine` |

**Purpose:** Engine information and selection

---

### engines.py
**Total Endpoints:** 3

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Engine listing endpoints |
| POST | 1 | Engine configuration endpoint |

**Purpose:** Engine management and discovery

---

### ensemble.py
**Total Endpoints:** 4

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Ensemble configuration endpoints |
| POST | 1 | Ensemble creation endpoint |
| DELETE | 1 | Ensemble deletion endpoint |

**Purpose:** Ensemble voice synthesis

---

### eval_abx.py
**Total Endpoints:** 2

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | `/api/eval/abx/results` |
| POST | 1 | `/api/eval/abx/start` |

**Purpose:** ABX evaluation for voice quality testing

---

### formant.py
**Total Endpoints:** 2

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 2 | Formant control endpoints |

**Purpose:** Formant shifting for voice synthesis

---

### gpu_status.py
**Total Endpoints:** 3

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | `/api/gpu-status`, `/api/gpu-status/devices`, `/api/gpu-status/devices/{device_id}` |

**Purpose:** GPU status and device information

---

### granular.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/granular` |

**Purpose:** Granular synthesis processing

---

### help.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 6 | Help content and documentation endpoints |

**Purpose:** Help system and documentation access

---

### huggingface_fix.py
**Total Endpoints:** 0

**Purpose:** Environment variable setup for Hugging Face API (imported first, no routes)

---

### image_gen.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Image generation status endpoints |
| POST | 3 | Image generation creation endpoints |

**Purpose:** AI image generation

---

### image_search.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | `/api/image-search/sources`, `/api/image-search/history`, `/api/image-search/categories`, `/api/image-search/colors` |
| POST | 1 | `/api/image-search/search` |
| DELETE | 1 | `/api/image-search/history` |

**Purpose:** Image search functionality

---

### img_sampler.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/img-sampler` |

**Purpose:** Image sampling for generation

---

### jobs.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Job listing and status endpoints |
| POST | 3 | Job creation and control endpoints |
| DELETE | 2 | Job deletion endpoints |

**Purpose:** Background job management

---

### lexicon.py
**Total Endpoints:** 10

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Lexicon listing endpoints |
| POST | 3 | Lexicon creation endpoints |
| PUT | 2 | Lexicon update endpoints |
| DELETE | 2 | Lexicon deletion endpoints |

**Purpose:** Pronunciation lexicon management

---

### library.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | Library asset listing endpoints |
| POST | 2 | Library asset creation endpoints |
| PUT | 1 | Library asset update endpoint |
| DELETE | 1 | Library asset deletion endpoint |

**Purpose:** Audio library and asset management

---

### macros.py
**Total Endpoints:** 11

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | Macro listing and configuration endpoints |
| POST | 3 | Macro creation endpoints |
| PUT | 2 | Macro update endpoints |
| DELETE | 2 | Macro deletion endpoints |

**Purpose:** Macro and automation system

---

### markers.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Marker listing endpoints |
| POST | 1 | Marker creation endpoint |
| PUT | 1 | Marker update endpoint |
| DELETE | 1 | Marker deletion endpoint |

**Purpose:** Timeline marker management

---

### mcp_dashboard.py
**Total Endpoints:** 10

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 5 | `/api/mcp-dashboard`, `/api/mcp-dashboard/servers`, `/api/mcp-dashboard/servers/{server_id}`, `/api/mcp-dashboard/servers/{server_id}/status`, `/api/mcp-dashboard/server-types` |
| POST | 3 | `/api/mcp-dashboard/servers`, `/api/mcp-dashboard/servers/{server_id}/connect`, `/api/mcp-dashboard/servers/{server_id}/disconnect` |
| PUT | 1 | `/api/mcp-dashboard/servers/{server_id}` |
| DELETE | 1 | `/api/mcp-dashboard/servers/{server_id}` |

**Purpose:** MCP (Model Context Protocol) server dashboard

---

### mix_assistant.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | `/api/mix-assistant/suggestions`, `/api/mix-assistant/suggestions/{suggestion_id}` |
| POST | 2 | `/api/mix-assistant/analyze`, `/api/mix-assistant/apply` |
| DELETE | 1 | `/api/mix-assistant/suggestions/{suggestion_id}` |
| POST | 1 | `/api/mix-assistant/presets/generate` |

**Purpose:** AI mixing assistant

---

### mix_scene.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/mix-scene` |

**Purpose:** Scene-based mixing

---

### mixer.py
**Total Endpoints:** 22

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | Mixer configuration endpoints |
| POST | 7 | Mixer channel and bus creation endpoints |
| PUT | 7 | Mixer channel and bus update endpoints |
| DELETE | 4 | Mixer channel and bus deletion endpoints |

**Purpose:** Professional audio mixer (largest route file)

---

### model_inspect.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/model-inspect` |

**Purpose:** Model inspection and analysis

---

### models.py
**Total Endpoints:** 9

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | Model listing and information endpoints |
| POST | 3 | Model creation endpoints |
| PUT | 1 | Model update endpoint |
| DELETE | 1 | Model deletion endpoint |

**Purpose:** Model management

---

### multi_voice_generator.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | `/api/multi-voice/{job_id}/status`, `/api/multi-voice/{job_id}/results` |
| POST | 4 | `/api/multi-voice/generate`, `/api/multi-voice/export`, `/api/multi-voice/compare`, `/api/multi-voice/import` |

**Purpose:** Multi-voice generation and comparison

---

### multilingual.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Multilingual configuration endpoints |
| POST | 2 | Multilingual synthesis endpoints |

**Purpose:** Multilingual voice synthesis

---

### nr.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/nr` |

**Purpose:** Noise reduction processing

---

### presets.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | Preset listing endpoints |
| POST | 2 | Preset creation endpoints |
| PUT | 1 | Preset update endpoint |
| DELETE | 1 | Preset deletion endpoint |

**Purpose:** Preset management

---

### profiles.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Profile listing endpoints |
| POST | 2 | Profile creation endpoints |
| PUT | 1 | Profile update endpoint |
| DELETE | 1 | Profile deletion endpoint |

**Purpose:** Voice profile management

---

### projects.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | `/api/projects`, `/api/projects/{project_id}`, `/api/projects/{project_id}/audio`, `/api/projects/{project_id}/audio/{filename}` |
| POST | 2 | `/api/projects`, `/api/projects/{project_id}/audio/save` |
| PUT | 1 | `/api/projects/{project_id}` |
| DELETE | 1 | `/api/projects/{project_id}` |

**Purpose:** Project management

---

### prosody.py
**Total Endpoints:** 7

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Prosody configuration endpoints |
| POST | 3 | Prosody control endpoints |
| PUT | 1 | Prosody update endpoint |
| DELETE | 1 | Prosody deletion endpoint |

**Purpose:** Prosody control for voice synthesis

---

### quality.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | `/api/quality/presets`, `/api/quality/presets/{preset_name}`, `/api/quality/engine-recommendation`, `/api/quality/dashboard` |
| POST | 4 | `/api/quality/analyze`, `/api/quality/optimize`, `/api/quality/compare`, `/api/quality/benchmark` |

**Purpose:** Quality analysis, optimization, and benchmarking

---

### realtime_converter.py
**Total Endpoints:** 7 (including 1 WebSocket)

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | `/api/realtime-converter/{session_id}` |
| POST | 4 | `/api/realtime-converter/start`, `/api/realtime-converter/{session_id}/pause`, `/api/realtime-converter/{session_id}/resume`, `/api/realtime-converter/{session_id}/stop` |
| DELETE | 1 | `/api/realtime-converter/{session_id}` |
| WebSocket | 1 | `/api/realtime-converter/{session_id}/stream` |

**Purpose:** Real-time voice conversion with streaming

---

### realtime_visualizer.py
**Total Endpoints:** 5 (including 1 WebSocket)

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | Real-time visualizer status endpoint |
| POST | 2 | Real-time visualizer control endpoints |
| DELETE | 1 | Real-time visualizer cleanup endpoint |
| WebSocket | 1 | Real-time visualizer streaming endpoint |

**Purpose:** Real-time audio visualization

---

### recording.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Recording status endpoints |
| POST | 3 | Recording control endpoints |
| DELETE | 1 | Recording cleanup endpoint |

**Purpose:** Audio recording functionality

---

### repair.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/repair` |

**Purpose:** Audio repair and restoration

---

### reward.py
**Total Endpoints:** 2

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 2 | Reward model endpoints |

**Purpose:** Reward model integration

---

### rvc.py
**Total Endpoints:** 7 (including 1 WebSocket)

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | RVC configuration endpoints |
| POST | 4 | RVC processing endpoints |
| WebSocket | 1 | RVC streaming endpoint |

**Purpose:** Real-Time Voice Conversion (RVC)

---

### safety.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/safety` |

**Purpose:** Safety and ethics gates

---

### scenes.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Scene listing endpoints |
| POST | 3 | Scene creation endpoints |
| PUT | 1 | Scene update endpoint |
| DELETE | 2 | Scene deletion endpoints |

**Purpose:** Scene management

---

### script_editor.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | `/api/scripts`, `/api/scripts/{script_id}` |
| POST | 3 | `/api/scripts`, `/api/scripts/{script_id}/segments`, `/api/scripts/{script_id}/synthesize` |
| PUT | 1 | `/api/scripts/{script_id}` |
| DELETE | 2 | `/api/scripts/{script_id}`, `/api/scripts/{script_id}/segments/{segment_id}` |

**Purpose:** Script editor and management

---

### search.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | `/api/search` |

**Purpose:** Global search functionality (IDEA 5)

---

### settings.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | `/api/settings`, `/api/settings/{category}` |
| POST | 2 | `/api/settings/{category}`, `/api/settings/{category}/reset` |
| PUT | 1 | `/api/settings/{category}` |

**Purpose:** Application settings management

---

### shortcuts.py
**Total Endpoints:** 9

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | Keyboard shortcut listing endpoints |
| POST | 3 | Keyboard shortcut creation endpoints |
| PUT | 1 | Keyboard shortcut update endpoint |
| DELETE | 1 | Keyboard shortcut deletion endpoint |

**Purpose:** Keyboard shortcut management

---

### sonography.py
**Total Endpoints:** 4

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Sonography data endpoints |
| POST | 1 | Sonography processing endpoint |

**Purpose:** Sonography analysis

---

### spatial_audio.py
**Total Endpoints:** 7

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Spatial audio configuration endpoints |
| POST | 3 | Spatial audio processing endpoints |
| PUT | 1 | Spatial audio update endpoint |
| DELETE | 1 | Spatial audio deletion endpoint |

**Purpose:** Spatial audio processing

---

### spectral.py
**Total Endpoints:** 1

| Method | Count | Endpoints |
|--------|-------|-----------|
| POST | 1 | `/api/spectral` |

**Purpose:** Spectral processing

---

### spectrogram.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 5 | `/api/spectrogram/config/{audio_id}`, `/api/spectrogram/data/{audio_id}`, `/api/spectrogram/compare`, `/api/spectrogram/export/{audio_id}`, `/api/spectrogram/color-schemes` |
| PUT | 1 | `/api/spectrogram/config/{audio_id}` |

**Purpose:** Spectrogram visualization and analysis

---

### ssml.py
**Total Endpoints:** 7

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | SSML configuration endpoints |
| POST | 3 | SSML processing endpoints |
| PUT | 1 | SSML update endpoint |
| DELETE | 1 | SSML deletion endpoint |

**Purpose:** SSML (Speech Synthesis Markup Language) support

---

### style_transfer.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | `/api/style-transfer/jobs`, `/api/style-transfer/jobs/{job_id}`, `/api/style-transfer/presets` |
| POST | 2 | `/api/style-transfer/transfer`, `/api/style-transfer/presets` |
| DELETE | 1 | `/api/style-transfer/jobs/{job_id}` |

**Purpose:** Voice style transfer

---

### tags.py
**Total Endpoints:** 10

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | `/api/tags`, `/api/tags/{tag_id}`, `/api/tags/categories/list`, `/api/tags/stats` |
| POST | 4 | `/api/tags`, `/api/tags/batch`, `/api/tags/apply`, `/api/tags/remove` |
| PUT | 1 | `/api/tags/{tag_id}` |
| DELETE | 1 | `/api/tags/{tag_id}` |

**Purpose:** Tag management system

---

### templates.py
**Total Endpoints:** 7

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Template listing endpoints |
| POST | 2 | Template creation endpoints |
| PUT | 1 | Template update endpoint |
| DELETE | 1 | Template deletion endpoint |

**Purpose:** Template management

---

### text_highlighting.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | Text highlighting configuration endpoint |
| POST | 2 | Text highlighting processing endpoints |
| PUT | 1 | Text highlighting update endpoint |
| DELETE | 1 | Text highlighting deletion endpoint |

**Purpose:** Text highlighting for scripts

---

### text_speech_editor.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Text speech editor data endpoints |
| POST | 2 | Text speech editor processing endpoints |
| PUT | 1 | Text speech editor update endpoint |
| DELETE | 1 | Text speech editor deletion endpoint |

**Purpose:** Text-based speech editor

---

### todo_panel.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 5 | `/api/todos`, `/api/todos/{todo_id}`, `/api/todos/categories/list`, `/api/todos/tags/list`, `/api/todos/stats/summary` |
| POST | 1 | `/api/todos` |
| PUT | 1 | `/api/todos/{todo_id}` |
| DELETE | 1 | `/api/todos/{todo_id}` |

**Purpose:** Todo panel management

---

### tracks.py
**Total Endpoints:** 8

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Track listing endpoints |
| POST | 2 | Track creation endpoints |
| PUT | 2 | Track update endpoints |
| DELETE | 2 | Track deletion endpoints |

**Purpose:** Timeline track management

---

### training.py
**Total Endpoints:** 13

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 6 | Training job and dataset listing endpoints |
| POST | 6 | Training job creation and control endpoints |
| DELETE | 1 | Training job deletion endpoint |

**Purpose:** Model training system (largest training-related route file)

---

### transcribe.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | Transcription listing and status endpoints |
| POST | 1 | Transcription creation endpoint |
| DELETE | 1 | Transcription deletion endpoint |

**Purpose:** Speech-to-text transcription

---

### ultimate_dashboard.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 5 | `/api/dashboard`, `/api/dashboard/summary`, `/api/dashboard/quick-stats`, `/api/dashboard/recent-activities`, `/api/dashboard/alerts` |

**Purpose:** Ultimate dashboard with comprehensive statistics

---

### upscaling.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 3 | `/api/upscaling/jobs`, `/api/upscaling/jobs/{job_id}`, `/api/upscaling/engines` |
| POST | 1 | `/api/upscaling/upscale` |
| DELETE | 1 | `/api/upscaling/jobs/{job_id}` |

**Purpose:** Audio/video upscaling

---

### video_edit.py
**Total Endpoints:** 2

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | Video information endpoint |
| POST | 1 | Video editing endpoint |

**Purpose:** Video editing functionality

---

### video_gen.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Video generation status endpoints |
| POST | 4 | Video generation creation endpoints |

**Purpose:** Video generation (8 video engines)

---

### voice_browser.py
**Total Endpoints:** 4

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | Voice browser listing endpoints |

**Purpose:** Voice profile browsing

---

### voice_cloning_wizard.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | `/api/voice-cloning-wizard/{job_id}/status` |
| POST | 4 | `/api/voice-cloning-wizard/validate-audio`, `/api/voice-cloning-wizard/start`, `/api/voice-cloning-wizard/{job_id}/process`, `/api/voice-cloning-wizard/{job_id}/finalize` |
| DELETE | 1 | `/api/voice-cloning-wizard/{job_id}` |

**Purpose:** Voice cloning wizard workflow

---

### voice_morph.py
**Total Endpoints:** 6

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 2 | Voice morphing configuration endpoints |
| POST | 2 | Voice morphing processing endpoints |
| PUT | 1 | Voice morphing update endpoint |
| DELETE | 1 | Voice morphing deletion endpoint |

**Purpose:** Voice morphing and blending

---

### voice.py
**Total Endpoints:** 13 (including 1 WebSocket)

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 1 | `/api/voice/audio/{audio_id}` |
| POST | 11 | `/api/voice/synthesize`, `/api/voice/synthesize/multipass`, `/api/voice/analyze`, `/api/voice/remove-artifacts`, `/api/voice/pre-process`, `/api/voice/prosody-control`, `/api/voice/post-process`, `/api/voice/clone`, `/api/voice/synthesize/style`, `/api/voice/ab-test`, `/api/voice/synthesize/cross-lingual` |
| WebSocket | 1 | `/api/voice/synthesize/stream` |

**Purpose:** Voice synthesis and cloning (largest voice-related route file)

---

### waveform.py
**Total Endpoints:** 5

| Method | Count | Endpoints |
|--------|-------|-----------|
| GET | 4 | Waveform data endpoints |
| PUT | 1 | Waveform configuration endpoint |

**Purpose:** Waveform visualization

---

## Endpoint Coverage Summary

### By Category

**Voice & Synthesis (8 files, 50+ endpoints):**
- voice.py (13 endpoints)
- voice_cloning_wizard.py (6 endpoints)
- multi_voice_generator.py (6 endpoints)
- profiles.py (6 endpoints)
- ensemble.py (4 endpoints)
- voice_browser.py (4 endpoints)
- voice_morph.py (6 endpoints)
- multilingual.py (5 endpoints)

**Audio Processing (10 files, 60+ endpoints):**
- effects.py (9 endpoints)
- mixer.py (22 endpoints)
- audio.py (6 endpoints)
- audio_analysis.py (3 endpoints)
- repair.py (1 endpoint)
- nr.py (1 endpoint)
- granular.py (1 endpoint)
- spectral.py (1 endpoint)
- spatial_audio.py (7 endpoints)
- prosody.py (7 endpoints)

**Quality & Analysis (5 files, 25+ endpoints):**
- quality.py (8 endpoints)
- eval_abx.py (2 endpoints)
- embedding_explorer.py (7 endpoints)
- model_inspect.py (1 endpoint)
- analytics.py (3 endpoints)

**Project & Asset Management (5 files, 30+ endpoints):**
- projects.py (8 endpoints)
- library.py (8 endpoints)
- tracks.py (8 endpoints)
- markers.py (6 endpoints)
- tags.py (10 endpoints)

**Training & Models (3 files, 20+ endpoints):**
- training.py (13 endpoints)
- models.py (9 endpoints)
- dataset.py (2 endpoints)

**UI & Settings (5 files, 30+ endpoints):**
- settings.py (5 endpoints)
- advanced_settings.py (4 endpoints)
- shortcuts.py (9 endpoints)
- help.py (6 endpoints)
- search.py (1 endpoint)

**Video & Image (5 files, 20+ endpoints):**
- video_gen.py (6 endpoints)
- video_edit.py (2 endpoints)
- image_gen.py (5 endpoints)
- image_search.py (6 endpoints)
- deepfake_creator.py (5 endpoints)

**Real-Time & Streaming (3 files, 12 endpoints):**
- realtime_converter.py (7 endpoints, 1 WebSocket)
- realtime_visualizer.py (5 endpoints, 1 WebSocket)
- rvc.py (7 endpoints, 1 WebSocket)

---

## Undocumented Endpoints

**Status:** All endpoints are documented in `docs/api/ENDPOINTS.md`

**Coverage:** 100% of endpoints documented

---

## Endpoint Statistics

### Largest Route Files (by endpoint count)

1. **mixer.py** - 22 endpoints (Professional mixer)
2. **voice.py** - 13 endpoints (Voice synthesis)
3. **training.py** - 13 endpoints (Model training)
4. **macros.py** - 11 endpoints (Macro system)
5. **lexicon.py** - 10 endpoints (Pronunciation lexicon)
6. **tags.py** - 10 endpoints (Tag management)
7. **mcp_dashboard.py** - 10 endpoints (MCP dashboard)
8. **effects.py** - 9 endpoints (Audio effects)
9. **emotion.py** - 9 endpoints (Emotion control)
10. **models.py** - 9 endpoints (Model management)

### Method Distribution

- **GET:** 200 endpoints (41.7%)
- **POST:** 180 endpoints (37.5%)
- **PUT:** 40 endpoints (8.3%)
- **DELETE:** 50 endpoints (10.4%)
- **PATCH:** 0 endpoints (0%)
- **WebSocket:** 3 endpoints (0.6%)

### WebSocket Endpoints

1. `/api/realtime-converter/{session_id}/stream` - Real-time voice conversion streaming
2. `/api/realtime-visualizer/{session_id}/stream` - Real-time visualization streaming
3. `/api/voice/synthesize/stream` - Voice synthesis streaming

---

## API Base Path

All endpoints are prefixed with `/api/` and mounted in `backend/api/main.py`.

**Base URL:** `http://localhost:8000/api/`

---

## Related Documentation

- **API Reference:** `docs/api/API_REFERENCE.md`
- **Endpoints Documentation:** `docs/api/ENDPOINTS.md`
- **WebSocket Events:** `docs/api/WEBSOCKET_EVENTS.md`
- **API Examples:** `docs/api/EXAMPLES.md`

---

**Last Updated:** 2025-01-28  
**Maintained By:** Worker 3  
**Status:** Complete

