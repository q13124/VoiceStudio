# Backend API Endpoint Test Report
## Comprehensive Testing of All 570 API Endpoints

**Date:** 2025-12-15 08:50:28  
**Worker:** Worker 3 (Testing/Quality/Documentation Specialist)  
**Test Suite:** Comprehensive API Endpoint Tests

---

## 📊 Executive Summary

**Total Route Files:** 100  
**Total Endpoints:** 570  
**Files with Code Quality Violations:** 28 (28.0%)  
**Endpoints with Implementation Issues:** 500 (87.7%)

---

## 📋 Endpoints by HTTP Method


### DELETE (58 endpoints)

| Path | File | Function | Implementation |
|------|------|----------|----------------|
| /api/advanced-spectrogram/views/{view_id} | advanced_spectrogram.py | delete_spectrogram_view | ❌ |
| /api/ai-production-assistant/session/{session_id} | ai_production_assistant.py | delete_session | ❌ |
| /api/api-key-manager/{key_id} | api_key_manager.py | delete_api_key | ❌ |
| /api/assistant/conversations/{conversation_id} | assistant.py | delete_conversation | ❌ |
| /api/automation/{curve_id} | automation.py | delete_automation_curve | ❌ |
| /api/automation/{curve_id}/points/{point_index} | automation.py | delete_automation_point | ❌ |
| /api/backup/{backup_id} | backup.py | delete_backup | ❌ |
| /api/batch/jobs/{job_id} | batch.py | delete_batch_job | ❌ |
| /api/deepfake-creator/jobs/{job_id} | deepfake_creator.py | delete_deepfake_job | ❌ |
| /api/effects/chains/{chain_id} | effects.py | delete_effect_chain | ✅ |
| /api/effects/presets/{preset_id} | effects.py | delete_effect_preset | ✅ |
| /api/embedding-explorer/embeddings/{embedding_id} | embedding_explorer.py | delete_embedding | ❌ |
| /api/emotion/preset/{preset_id} | emotion.py | delete_preset | ❌ |
| /api/ensemble/{job_id} | ensemble.py | delete_ensemble_job | ❌ |
| /api/image-search/history | image_search.py | clear_search_history | ❌ |
| /api/jobs/{job_id} | jobs.py | delete_job | ❌ |
| /api/lexicon/lexicons/{lexicon_id} | lexicon.py | delete_lexicon | ❌ |
| /api/lexicon/lexicons/{lexicon_id}/entries/{word} | lexicon.py | delete_lexicon_entry | ❌ |
| /api/lexicon/remove/{word} | lexicon.py | remove_lexicon_entry | ❌ |
| /api/library/assets/{asset_id} | library.py | delete_asset | ❌ |
| /api/macros/automation/curves/{curve_id} | macros.py | delete_automation_curve | ✅ |
| /api/macros/{macro_id} | macros.py | delete_macro | ✅ |
| /api/macros/{macro_id}/schedule | macros.py | cancel_macro_schedule | ❌ |
| /api/markers/{marker_id} | markers.py | delete_marker | ❌ |
| /api/mcp-dashboard/servers/{server_id} | mcp_dashboard.py | delete_mcp_server | ❌ |
| /api/mix-assistant/suggestions/{suggestion_id} | mix_assistant.py | dismiss_suggestion | ❌ |
| /api/mixer/presets/{project_id}/{preset_id} | mixer.py | delete_preset | ❌ |
| /api/mixer/state/{project_id}/returns/{return_id} | mixer.py | delete_return | ❌ |
| /api/mixer/state/{project_id}/sends/{send_id} | mixer.py | delete_send | ❌ |
| /api/mixer/state/{project_id}/subgroups/{subgroup_id} | mixer.py | delete_subgroup | ❌ |
| /api/models/{engine}/{model_name} | models.py | delete_model | ❌ |
| /api/presets/{preset_id} | presets.py | delete_preset | ❌ |
| /api/profiles/{profile_id} | profiles.py | delete_profile | ✅ |
| /api/projects/{project_id} | projects.py | delete_project | ✅ |
| /api/prosody/configs/{config_id} | prosody.py | delete_prosody_config | ❌ |
| /api/realtime-converter/{session_id} | realtime_converter.py | delete_converter_session | ❌ |
| /api/realtime-visualizer/{session_id} | realtime_visualizer.py | delete_visualizer_session | ❌ |
| /api/recording/{recording_id} | recording.py | cancel_recording | ❌ |
| /api/scenes/{scene_id} | scenes.py | delete_scene | ❌ |
| /api/scenes/{scene_id}/tracks/{track_id} | scenes.py | remove_track_from_scene | ❌ |
| /api/script-editor/{script_id} | script_editor.py | delete_script | ❌ |
| /api/script-editor/{script_id}/segments/{segment_id} | script_editor.py | remove_segment_from_script | ❌ |
| /api/shortcuts/{shortcut_id} | shortcuts.py | delete_shortcut | ❌ |
| /api/spatial-audio/configs/{config_id} | spatial_audio.py | delete_spatial_config | ❌ |
| /api/ssml/{document_id} | ssml.py | delete_ssml_document | ❌ |
| /api/style-transfer/jobs/{job_id} | style_transfer.py | delete_style_transfer_job | ❌ |
| /api/tags/{tag_id} | tags.py | delete_tag | ❌ |
| /api/templates/{template_id} | templates.py | delete_template | ❌ |
| /api/text-highlighting/{session_id} | text_highlighting.py | delete_highlighting_session | ❌ |
| /api/todo-panel/{todo_id} | todo_panel.py | delete_todo | ❌ |
| /api/tracks/{track_id} | tracks.py | delete_track | ✅ |
| /api/tracks/{track_id}/clips/{clip_id} | tracks.py | delete_clip | ✅ |
| /api/training/{training_id} | training.py | delete_training_job | ❌ |
| /api/transcribe/{transcription_id} | transcribe.py | delete_transcription | ❌ |
| /api/upscaling/jobs/{job_id} | upscaling.py | delete_upscaling_job | ❌ |
| /api/voice-cloning-wizard/{job_id} | voice_cloning_wizard.py | delete_wizard_job | ❌ |
| /api/voice-morph/configs/{config_id} | voice_morph.py | delete_morph_config | ❌ |
| /api/workflows/{workflow_id} | workflows.py | delete_workflow | ❌ |

### GET (250 endpoints)

| Path | File | Function | Implementation |
|------|------|----------|----------------|
| /api/advanced-settings/category/{category} | advanced_settings.py | get_settings_category | ❌ |
| /api/advanced-spectrogram/export/{view_id} | advanced_spectrogram.py | export_spectrogram | ❌ |
| /api/advanced-spectrogram/view-types | advanced_spectrogram.py | get_view_types | ❌ |
| /api/advanced-spectrogram/views/{view_id} | advanced_spectrogram.py | get_spectrogram_view | ❌ |
| /api/ai-production-assistant/context | ai_production_assistant.py | get_context | ❌ |
| /api/ai-production-assistant/session/{session_id} | ai_production_assistant.py | get_session | ❌ |
| /api/analytics/categories | analytics.py | list_analytics_categories | ❌ |
| /api/analytics/explain-quality | analytics.py | explain_quality_prediction | ❌ |
| /api/analytics/export/metrics/{category} | analytics.py | export_category_metrics | ❌ |
| /api/analytics/export/summary | analytics.py | export_analytics_summary | ❌ |
| /api/analytics/metrics/{category} | analytics.py | get_category_metrics | ❌ |
| /api/analytics/summary | analytics.py | get_analytics_summary | ❌ |
| /api/analytics/visualize-quality | analytics.py | visualize_quality_metrics | ❌ |
| /api/api-key-manager/services/list | api_key_manager.py | list_supported_services | ❌ |
| /api/api-key-manager/{key_id} | api_key_manager.py | get_api_key | ❌ |
| /api/assistant-run/actions | assistant_run.py | list_actions | ❌ |
| /api/assistant-run/actions/{action_id} | assistant_run.py | get_action | ❌ |
| /api/assistant/conversations | assistant.py | list_conversations | ❌ |
| /api/assistant/conversations/{conversation_id} | assistant.py | get_conversation | ❌ |
| /api/audio-analysis/{audio_id} | audio_analysis.py | get_audio_analysis | ❌ |
| /api/audio-analysis/{audio_id}/compare | audio_analysis.py | compare_audio_analysis | ❌ |
| /api/audio-analysis/{audio_id}/metadata | audio_analysis.py | get_audio_metadata | ❌ |
| /api/audio-analysis/{audio_id}/pitch | audio_analysis.py | get_pitch_analysis | ❌ |
| /api/audio-analysis/{audio_id}/wavelet | audio_analysis.py | get_wavelet_analysis | ❌ |
| /api/audio-audit/all | audio_audit.py | audit_all_modules | ✅ |
| /api/audio-audit/needing-attention | audio_audit.py | get_modules_needing_attention | ✅ |
| /api/audio-audit/report | audio_audit.py | generate_enhancement_report | ✅ |
| /api/audio-audit/summary | audio_audit.py | get_audit_summary | ✅ |
| /api/audio/loudness | audio.py | get_loudness_data | ✅ |
| /api/audio/meters | audio.py | get_audio_meters | ✅ |
| /api/audio/phase | audio.py | get_phase_data | ✅ |
| /api/audio/radar | audio.py | get_radar_data | ✅ |
| /api/audio/spectrogram | audio.py | get_spectrogram_data | ✅ |
| /api/audio/waveform | audio.py | get_waveform_data | ✅ |
| /api/auth/me | auth.py | get_current_user_info | ❌ |
| /api/automation/tracks/{track_id}/parameters | automation.py | get_track_parameters | ❌ |
| /api/automation/{curve_id} | automation.py | get_automation_curve | ❌ |
| /api/backup/{backup_id} | backup.py | get_backup_info | ❌ |
| /api/backup/{backup_id}/download | backup.py | download_backup | ❌ |
| /api/batch/jobs | batch.py | list_batch_jobs | ❌ |
| /api/batch/jobs/{job_id} | batch.py | get_batch_job | ❌ |
| /api/batch/jobs/{job_id}/quality | batch.py | get_batch_job_quality | ❌ |
| /api/batch/jobs/{job_id}/quality-report | batch.py | get_batch_quality_report | ❌ |
| /api/batch/quality/statistics | batch.py | get_batch_quality_statistics | ❌ |
| /api/batch/queue/status | batch.py | get_queue_status | ❌ |
| /api/dataset-editor/{dataset_id} | dataset_editor.py | get_dataset_detail | ❌ |
| /api/deepfake-creator/engines | deepfake_creator.py | list_deepfake_engines | ❌ |
| /api/deepfake-creator/jobs | deepfake_creator.py | list_deepfake_jobs | ❌ |
| /api/deepfake-creator/jobs/{job_id} | deepfake_creator.py | get_deepfake_job | ❌ |
| /api/deepfake-creator/queue/status | deepfake_creator.py | get_queue_status | ❌ |
| /api/docs/openapi.json | docs.py | get_openapi_schema | ✅ |
| /api/docs/stats | docs.py | get_documentation_stats | ✅ |
| /api/docs/validate | docs.py | validate_api_documentation | ✅ |
| /api/effects/chains | effects.py | list_effect_chains | ✅ |
| /api/effects/chains/{chain_id} | effects.py | get_effect_chain | ✅ |
| /api/effects/presets | effects.py | list_effect_presets | ✅ |
| /api/embedding-explorer/embeddings | embedding_explorer.py | list_embeddings | ❌ |
| /api/embedding-explorer/embeddings/{embedding_id} | embedding_explorer.py | get_embedding | ❌ |
| /api/emotion-style/emotions | emotion_style.py | get_emotion_presets | ❌ |
| /api/emotion-style/styles | emotion_style.py | get_style_presets | ❌ |
| /api/emotion/list | emotion.py | list_emotions | ❌ |
| /api/emotion/preset/list | emotion.py | list_presets | ❌ |
| /api/emotion/preset/{preset_id} | emotion.py | get_preset | ❌ |
| /api/engine-audit/all | engine_audit.py | audit_all_engines | ✅ |
| /api/engine-audit/needing-attention | engine_audit.py | get_engines_needing_attention | ✅ |
| /api/engine-audit/report | engine_audit.py | generate_enhancement_report | ✅ |
| /api/engine-audit/summary | engine_audit.py | get_audit_summary | ✅ |
| /api/engine/telemetry | engine.py | telemetry | ❌ |
| /api/engine/telemetry/history | engine.py | get_telemetry_history | ❌ |
| /api/engines/compare | engines.py | compare_engines | ❌ |
| /api/engines/list | engines.py | list_engines | ❌ |
| /api/ensemble/multi-engine/{job_id} | ensemble.py | get_multi_engine_ensemble_status | ❌ |
| /api/ensemble/{job_id} | ensemble.py | get_ensemble_status | ❌ |
| /api/eval-abx/results | eval_abx.py | results | ❌ |
| /api/eval-abx/sessions/{session_id} | eval_abx.py | get_session | ❌ |
| /api/gpu-status/devices | gpu_status.py | list_gpu_devices | ❌ |
| /api/gpu-status/devices/{device_id} | gpu_status.py | get_gpu_device | ❌ |
| /api/health/ | health.py | health_check | ❌ |
| /api/health/detailed | health.py | detailed_health_check | ❌ |
| /api/health/engines | health.py | engine_health | ✅ |
| /api/health/liveness | health.py | liveness_check | ✅ |
| /api/health/performance | health.py | performance_metrics | ✅ |
| /api/health/performance/{endpoint:path} | health.py | endpoint_performance_metrics | ✅ |
| /api/health/readiness | health.py | readiness_check | ❌ |
| /api/health/resources | health.py | resource_usage | ✅ |
| /api/health/simple | health.py | simple_health_check | ✅ |
| /api/help/categories | help.py | get_help_categories | ❌ |
| /api/help/panel/{panel_id} | help.py | get_panel_help | ❌ |
| /api/help/search | help.py | search_help | ❌ |
| /api/help/shortcuts | help.py | get_keyboard_shortcuts | ❌ |
| /api/help/topics | help.py | get_help_topics | ❌ |
| /api/help/topics/{topic_id} | help.py | get_help_topic | ❌ |
| /api/image-gen/engines/list | image_gen.py | list_engines | ❌ |
| /api/image-gen/{image_id} | image_gen.py | get_image | ❌ |
| /api/image-search/categories | image_search.py | list_categories | ❌ |
| /api/image-search/colors | image_search.py | list_colors | ❌ |
| /api/image-search/history | image_search.py | get_search_history | ❌ |
| /api/image-search/sources | image_search.py | list_image_sources | ❌ |
| /api/img-sampler/samplers | img_sampler.py | list_samplers | ❌ |
| /api/img-sampler/samplers/{sampler_name} | img_sampler.py | get_sampler_info | ❌ |
| /api/jobs/summary | jobs.py | get_job_summary | ❌ |
| /api/jobs/{job_id} | jobs.py | get_job | ❌ |
| /api/lexicon/lexicons | lexicon.py | list_lexicons | ❌ |
| /api/lexicon/lexicons/{lexicon_id} | lexicon.py | get_lexicon | ❌ |
| /api/lexicon/lexicons/{lexicon_id}/entries | lexicon.py | list_lexicon_entries | ❌ |
| /api/lexicon/list | lexicon.py | list_lexicon_entries | ❌ |
| /api/library/assets | library.py | search_assets | ❌ |
| /api/library/assets/{asset_id} | library.py | get_asset | ❌ |
| /api/library/folders | library.py | get_folders | ❌ |
| /api/library/types | library.py | get_asset_types | ❌ |
| /api/macros/automation/curves | macros.py | list_automation_curves | ✅ |
| /api/macros/{macro_id} | macros.py | get_macro | ✅ |
| /api/macros/{macro_id}/schedule | macros.py | get_macro_schedule | ❌ |
| /api/macros/{macro_id}/status | macros.py | get_macro_execution_status | ✅ |
| /api/markers/categories/list | markers.py | get_categories | ❌ |
| /api/markers/{marker_id} | markers.py | get_marker | ❌ |
| /api/mcp-dashboard/server-types | mcp_dashboard.py | list_server_types | ❌ |
| /api/mcp-dashboard/servers | mcp_dashboard.py | list_mcp_servers | ❌ |
| /api/mcp-dashboard/servers/{server_id} | mcp_dashboard.py | get_mcp_server | ❌ |
| /api/mix-assistant/suggestions | mix_assistant.py | list_suggestions | ❌ |
| /api/mix-assistant/suggestions/{suggestion_id} | mix_assistant.py | get_suggestion | ❌ |
| /api/mixer/meters/{project_id} | mixer.py | get_mixer_meters | ❌ |
| /api/mixer/presets/{project_id} | mixer.py | list_presets | ❌ |
| /api/mixer/presets/{project_id}/{preset_id} | mixer.py | get_preset | ❌ |
| /api/mixer/state/{project_id} | mixer.py | get_mixer_state | ❌ |
| /api/ml-optimization/methods | ml_optimization.py | get_available_methods | ❌ |
| /api/model-inspect/inspect/layers | model_inspect.py | list_layers | ❌ |
| /api/models/stats/cache | models.py | get_cache_stats | ❌ |
| /api/models/stats/storage | models.py | get_storage_stats | ❌ |
| /api/models/{engine}/{model_name} | models.py | get_model | ❌ |
| /api/models/{engine}/{model_name}/export | models.py | export_model | ❌ |
| /api/monitoring/errors | monitoring.py | get_errors | ✅ |
| /api/monitoring/errors/{error_type} | monitoring.py | get_errors_by_type | ✅ |
| /api/monitoring/metrics | monitoring.py | get_metrics | ✅ |
| /api/monitoring/metrics/counters | monitoring.py | get_counters | ✅ |
| /api/monitoring/metrics/gauges | monitoring.py | get_gauges | ✅ |
| /api/monitoring/metrics/histograms/{name} | monitoring.py | get_histogram_stats | ✅ |
| /api/monitoring/metrics/timers/{name} | monitoring.py | get_timer_stats | ✅ |
| /api/multi-voice-generator/{job_id}/results | multi_voice_generator.py | get_multi_voice_results | ❌ |
| /api/multi-voice-generator/{job_id}/status | multi_voice_generator.py | get_multi_voice_status | ❌ |
| /api/multilingual/languages | multilingual.py | get_language_configs | ❌ |
| /api/multilingual/languages/{config_id} | multilingual.py | get_language_config | ❌ |
| /api/multilingual/supported | multilingual.py | get_supported_languages | ❌ |
| /api/nr/noise-prints | nr.py | list_noise_prints | ❌ |
| /api/plugins/{plugin_id} | plugins.py | get_plugin | ❌ |
| /api/plugins/{plugin_id}/config | plugins.py | get_plugin_config | ❌ |
| /api/plugins/{plugin_id}/manifest | plugins.py | get_plugin_manifest | ❌ |
| /api/presets/ | presets.py | search_presets | ❌ |
| /api/presets/categories/{preset_type} | presets.py | get_categories | ❌ |
| /api/presets/types | presets.py | get_preset_types | ❌ |
| /api/presets/{preset_id} | presets.py | get_preset | ❌ |
| /api/profiles/{profile_id} | profiles.py | get_profile | ✅ |
| /api/projects/{project_id} | projects.py | get_project | ✅ |
| /api/projects/{project_id}/audio | projects.py | list_project_audio | ✅ |
| /api/projects/{project_id}/audio/{filename} | projects.py | get_project_audio | ✅ |
| /api/prosody/configs | prosody.py | list_prosody_configs | ❌ |
| /api/prosody/configs/{config_id} | prosody.py | get_prosody_config | ❌ |
| /api/quality-pipelines/engines/{engine_id}/presets | quality_pipelines.py | list_presets | ❌ |
| /api/quality/baseline/{profile_id} | quality.py | get_quality_baseline | ❌ |
| /api/quality/consistency/all | quality.py | check_all_projects_consistency | ❌ |
| /api/quality/consistency/{project_id} | quality.py | check_project_consistency | ❌ |
| /api/quality/consistency/{project_id}/trends | quality.py | get_project_quality_trends | ❌ |
| /api/quality/dashboard | quality.py | get_quality_dashboard | ❌ |
| /api/quality/degradation/{profile_id} | quality.py | check_quality_degradation | ❌ |
| /api/quality/engine-recommendation | quality.py | get_engine_recommendation | ❌ |
| /api/quality/history/{profile_id} | quality.py | get_quality_history | ❌ |
| /api/quality/history/{profile_id}/trends | quality.py | get_quality_trends | ❌ |
| /api/quality/presets | quality.py | list_presets | ❌ |
| /api/quality/presets/{preset_name} | quality.py | get_preset | ❌ |
| /api/realtime-converter/{session_id} | realtime_converter.py | get_converter_session | ❌ |
| /api/realtime-visualizer/{session_id} | realtime_visualizer.py | get_visualizer_session | ❌ |
| /api/recording/devices | recording.py | get_recording_devices | ❌ |
| /api/recording/{recording_id}/status | recording.py | get_recording_status | ❌ |
| /api/reward/jobs/{job_id} | reward.py | get_training_job | ❌ |
| /api/reward/models | reward.py | list_models | ❌ |
| /api/rvc/audio/{audio_id} | rvc.py | get_audio | ❌ |
| /api/rvc/models | rvc.py | get_models | ❌ |
| /api/safety/categories | safety.py | get_safety_categories | ❌ |
| /api/scenes/{scene_id} | scenes.py | get_scene | ❌ |
| /api/script-editor/{script_id} | script_editor.py | get_script | ❌ |
| /api/settings/{category} | settings.py | get_settings_category | ❌ |
| /api/shortcuts/categories | shortcuts.py | get_shortcut_categories | ❌ |
| /api/shortcuts/check-conflict | shortcuts.py | check_conflict | ❌ |
| /api/shortcuts/{shortcut_id} | shortcuts.py | get_shortcut | ❌ |
| /api/sonography/color-schemes | sonography.py | get_available_color_schemes | ❌ |
| /api/sonography/perspectives | sonography.py | get_available_perspectives | ❌ |
| /api/sonography/{audio_id} | sonography.py | get_sonography_data | ❌ |
| /api/spatial-audio/configs | spatial_audio.py | list_spatial_configs | ❌ |
| /api/spatial-audio/configs/{config_id} | spatial_audio.py | get_spatial_config | ❌ |
| /api/spectrogram/color-schemes | spectrogram.py | get_color_schemes | ❌ |
| /api/spectrogram/compare | spectrogram.py | compare_spectrograms | ❌ |
| /api/spectrogram/config/{audio_id} | spectrogram.py | get_spectrogram_config | ❌ |
| /api/spectrogram/data/{audio_id} | spectrogram.py | get_spectrogram_data | ❌ |
| /api/spectrogram/export/{audio_id} | spectrogram.py | export_spectrogram | ❌ |
| /api/ssml/{document_id} | ssml.py | get_ssml_document | ❌ |
| /api/style-transfer/jobs | style_transfer.py | list_style_transfer_jobs | ❌ |
| /api/style-transfer/jobs/{job_id} | style_transfer.py | get_style_transfer_job | ❌ |
| /api/style-transfer/presets | style_transfer.py | list_style_presets | ❌ |
| /api/tags/categories/list | tags.py | get_tag_categories | ❌ |
| /api/tags/{tag_id} | tags.py | get_tag | ❌ |
| /api/tags/{tag_id}/usage | tags.py | get_tag_usage | ❌ |
| /api/templates/categories/list | templates.py | get_template_categories | ❌ |
| /api/templates/{template_id} | templates.py | get_template | ❌ |
| /api/text-highlighting/{session_id} | text_highlighting.py | get_highlighting_session | ❌ |
| /api/text-speech-editor/session/{session_id} | text_speech_editor.py | get_edit_session | ❌ |
| /api/todo-panel/categories/list | todo_panel.py | list_categories | ❌ |
| /api/todo-panel/export | todo_panel.py | export_todos | ❌ |
| /api/todo-panel/stats/summary | todo_panel.py | get_todo_summary | ❌ |
| /api/todo-panel/tags/list | todo_panel.py | list_tags | ❌ |
| /api/todo-panel/{todo_id} | todo_panel.py | get_todo | ❌ |
| /api/tracks/{track_id} | tracks.py | get_track | ✅ |
| /api/training-audit/all | training_audit.py | audit_all_modules | ✅ |
| /api/training-audit/needing-attention | training_audit.py | get_modules_needing_attention | ✅ |
| /api/training-audit/report | training_audit.py | generate_enhancement_report | ✅ |
| /api/training-audit/summary | training_audit.py | get_audit_summary | ✅ |
| /api/training/datasets | training.py | list_datasets | ❌ |
| /api/training/datasets/{dataset_id} | training.py | get_dataset | ❌ |
| /api/training/exports/{export_id}/download | training.py | download_export | ❌ |
| /api/training/logs/{training_id} | training.py | get_training_logs | ❌ |
| /api/training/status | training.py | list_training_jobs | ❌ |
| /api/training/status/{training_id} | training.py | get_training_status | ❌ |
| /api/transcribe/ | transcribe.py | list_transcriptions | ❌ |
| /api/transcribe/languages | transcribe.py | get_supported_languages | ❌ |
| /api/transcribe/{transcription_id} | transcribe.py | get_transcription | ❌ |
| /api/ultimate-dashboard/alerts | ultimate_dashboard.py | get_system_alerts | ❌ |
| /api/ultimate-dashboard/quick-stats | ultimate_dashboard.py | get_quick_stats | ❌ |
| /api/ultimate-dashboard/recent-activities | ultimate_dashboard.py | get_recent_activities | ❌ |
| /api/ultimate-dashboard/summary | ultimate_dashboard.py | get_dashboard_summary | ❌ |
| /api/upscaling/engines | upscaling.py | list_upscaling_engines | ❌ |
| /api/upscaling/export/{job_id} | upscaling.py | export_upscaled_media | ❌ |
| /api/upscaling/jobs | upscaling.py | list_upscaling_jobs | ❌ |
| /api/upscaling/jobs/{job_id} | upscaling.py | get_upscaling_job | ❌ |
| /api/video-edit/info | video_edit.py | get_video_info_endpoint | ❌ |
| /api/video-gen/engines/list | video_gen.py | list_engines | ❌ |
| /api/video-gen/{video_id} | video_gen.py | get_video | ❌ |
| /api/voice-browser/languages | voice_browser.py | get_available_languages | ❌ |
| /api/voice-browser/tags | voice_browser.py | get_available_tags | ❌ |
| /api/voice-browser/voices | voice_browser.py | search_voices | ❌ |
| /api/voice-browser/voices/{voice_id} | voice_browser.py | get_voice_summary | ❌ |
| /api/voice-cloning-wizard/{job_id}/status | voice_cloning_wizard.py | get_wizard_status | ❌ |
| /api/voice-morph/configs | voice_morph.py | list_morph_configs | ❌ |
| /api/voice-morph/configs/{config_id} | voice_morph.py | get_morph_config | ❌ |
| /api/voice-speech/backends | voice_speech.py | get_available_backends | ❌ |
| /api/voice-speech/{audio_id}/voice-activity | voice_speech.py | detect_voice_activity | ❌ |
| /api/voice/audio/{audio_id} | voice.py | get_audio | ❌ |
| /api/waveform/analysis/{audio_id} | waveform.py | analyze_waveform | ❌ |
| /api/waveform/compare | waveform.py | compare_waveforms | ❌ |
| /api/waveform/config/{audio_id} | waveform.py | get_waveform_config | ❌ |
| /api/waveform/data/{audio_id} | waveform.py | get_waveform_data | ❌ |
| /api/workflows/{workflow_id} | workflows.py | get_workflow | ❌ |

### POST (222 endpoints)

| Path | File | Function | Implementation |
|------|------|----------|----------------|
| /api/adr/align | adr.py | align | ❌ |
| /api/advanced-settings/reset | advanced_settings.py | reset_advanced_settings | ❌ |
| /api/advanced-spectrogram/compare | advanced_spectrogram.py | compare_spectrograms | ❌ |
| /api/advanced-spectrogram/generate | advanced_spectrogram.py | generate_advanced_spectrogram | ❌ |
| /api/ai-production-assistant/execute | ai_production_assistant.py | execute_command | ❌ |
| /api/ai-production-assistant/query | ai_production_assistant.py | process_query | ❌ |
| /api/api-key-manager/{key_id}/validate | api_key_manager.py | validate_api_key | ❌ |
| /api/articulation/analyze | articulation.py | analyze | ❌ |
| /api/assistant-run/run | assistant_run.py | run | ❌ |
| /api/assistant/chat | assistant.py | chat_with_assistant | ❌ |
| /api/assistant/suggest-tasks | assistant.py | suggest_tasks | ❌ |
| /api/audio-analysis/{audio_id}/analyze | audio_analysis.py | analyze_audio | ❌ |
| /api/auth/api-keys/generate | auth.py | generate_api_key | ❌ |
| /api/auth/api-keys/revoke | auth.py | revoke_api_key | ❌ |
| /api/auth/login | auth.py | login | ❌ |
| /api/auth/refresh | auth.py | refresh_token | ❌ |
| /api/auth/users | auth.py | create_user | ❌ |
| /api/automation/{curve_id}/points | automation.py | add_automation_point | ❌ |
| /api/backup/upload | backup.py | upload_backup | ❌ |
| /api/backup/{backup_id}/restore | backup.py | restore_backup | ❌ |
| /api/batch/jobs | batch.py | create_batch_job | ❌ |
| /api/batch/jobs/{job_id}/cancel | batch.py | cancel_batch_job | ❌ |
| /api/batch/jobs/{job_id}/retry-with-quality | batch.py | retry_batch_job_with_quality | ❌ |
| /api/batch/jobs/{job_id}/start | batch.py | start_batch_job | ❌ |
| /api/dataset-editor/{dataset_id}/audio | dataset_editor.py | add_audio_to_dataset | ❌ |
| /api/dataset-editor/{dataset_id}/validate | dataset_editor.py | validate_dataset | ❌ |
| /api/dataset/analyze | dataset.py | analyze_dataset | ❌ |
| /api/dataset/cull | dataset.py | cull | ❌ |
| /api/dataset/export | dataset.py | export_dataset | ❌ |
| /api/dataset/score | dataset.py | score | ❌ |
| /api/dataset/validate | dataset.py | validate_dataset | ❌ |
| /api/deepfake-creator/create | deepfake_creator.py | create_deepfake | ❌ |
| /api/dubbing/sync | dubbing.py | sync | ❌ |
| /api/dubbing/translate | dubbing.py | translate | ❌ |
| /api/effects/chains | effects.py | create_effect_chain | ✅ |
| /api/effects/chains/{chain_id}/process | effects.py | process_audio_with_chain | ✅ |
| /api/effects/presets | effects.py | create_effect_preset | ✅ |
| /api/embedding-explorer/cluster | embedding_explorer.py | cluster_embeddings | ❌ |
| /api/embedding-explorer/compare | embedding_explorer.py | compare_embeddings | ❌ |
| /api/embedding-explorer/extract | embedding_explorer.py | extract_embedding | ❌ |
| /api/embedding-explorer/visualize | embedding_explorer.py | visualize_embeddings | ❌ |
| /api/emotion-style/apply | emotion_style.py | apply_emotion_style | ❌ |
| /api/emotion/analyze | emotion.py | analyze | ❌ |
| /api/emotion/apply | emotion.py | apply | ❌ |
| /api/emotion/apply-extended | emotion.py | apply_extended | ❌ |
| /api/emotion/preset/save | emotion.py | save_preset | ❌ |
| /api/engine/telemetry/record | engine.py | record_telemetry | ❌ |
| /api/engines/recommend | engines.py | recommend_engine | ❌ |
| /api/ensemble/multi-engine | ensemble.py | create_multi_engine_ensemble | ❌ |
| /api/eval-abx/sessions/{session_id}/complete | eval_abx.py | complete_session | ❌ |
| /api/eval-abx/start | eval_abx.py | start | ❌ |
| /api/eval-abx/submit | eval_abx.py | submit_result | ❌ |
| /api/formant/analyze | formant.py | analyze | ❌ |
| /api/formant/apply | formant.py | apply | ❌ |
| /api/granular/render | granular.py | render | ❌ |
| /api/image-gen/enhance-face | image_gen.py | enhance_face | ❌ |
| /api/image-gen/generate | image_gen.py | generate_image | ❌ |
| /api/image-gen/upscale | image_gen.py | upscale_image | ❌ |
| /api/image-search/search | image_search.py | search_images | ❌ |
| /api/img-sampler/render | img_sampler.py | render | ❌ |
| /api/jobs/{job_id}/cancel | jobs.py | cancel_job | ❌ |
| /api/jobs/{job_id}/pause | jobs.py | pause_job | ❌ |
| /api/jobs/{job_id}/resume | jobs.py | resume_job | ❌ |
| /api/lexicon/add | lexicon.py | add_lexicon_entry | ❌ |
| /api/lexicon/lexicons | lexicon.py | create_lexicon | ❌ |
| /api/lexicon/lexicons/{lexicon_id}/entries | lexicon.py | create_lexicon_entry | ❌ |
| /api/lexicon/phoneme | lexicon.py | estimate_phonemes | ❌ |
| /api/lexicon/search | lexicon.py | search_lexicon_entries | ❌ |
| /api/library/assets | library.py | create_asset | ❌ |
| /api/library/folders | library.py | create_folder | ❌ |
| /api/macros/automation/curves | macros.py | create_automation_curve | ✅ |
| /api/macros/{macro_id}/execute | macros.py | execute_macro | ✅ |
| /api/macros/{macro_id}/schedule | macros.py | schedule_macro | ❌ |
| /api/mcp-dashboard/servers | mcp_dashboard.py | create_mcp_server | ❌ |
| /api/mcp-dashboard/servers/{server_id}/connect | mcp_dashboard.py | connect_mcp_server | ❌ |
| /api/mix-assistant/analyze | mix_assistant.py | analyze_mix | ❌ |
| /api/mix-assistant/apply | mix_assistant.py | apply_suggestions | ❌ |
| /api/mix-assistant/master/analyze | mix_assistant.py | analyze_mastering | ❌ |
| /api/mix-assistant/master/apply | mix_assistant.py | apply_mastering | ❌ |
| /api/mix-assistant/mix/analyze | mix_assistant.py | analyze_mix_simple | ❌ |
| /api/mix-assistant/mix/apply | mix_assistant.py | apply_mix_suggestions_simple | ❌ |
| /api/mix-assistant/mix/suggest | mix_assistant.py | get_mix_suggestions_simple | ❌ |
| /api/mix-assistant/presets/generate | mix_assistant.py | generate_preset | ❌ |
| /api/mix-scene/analyze | mix_scene.py | analyze | ✅ |
| /api/mixer/meters/{project_id}/simulate | mixer.py | simulate_meter_updates | ❌ |
| /api/mixer/presets/{project_id} | mixer.py | create_preset | ❌ |
| /api/mixer/presets/{project_id}/{preset_id}/apply | mixer.py | apply_preset | ❌ |
| /api/mixer/state/{project_id}/reset | mixer.py | reset_mixer_state | ❌ |
| /api/mixer/state/{project_id}/returns | mixer.py | create_return | ❌ |
| /api/mixer/state/{project_id}/sends | mixer.py | create_send | ❌ |
| /api/mixer/state/{project_id}/subgroups | mixer.py | create_subgroup | ❌ |
| /api/ml-optimization/explain | ml_optimization.py | explain_model | ❌ |
| /api/ml-optimization/optimize | ml_optimization.py | optimize_hyperparameters | ❌ |
| /api/model-inspect/inspect | model_inspect.py | inspect | ❌ |
| /api/models/import | models.py | import_model | ❌ |
| /api/models/{engine}/{model_name}/verify | models.py | verify_model | ❌ |
| /api/monitoring/errors/clear | monitoring.py | clear_errors | ✅ |
| /api/monitoring/metrics/clear | monitoring.py | clear_metrics | ✅ |
| /api/multi-voice-generator/compare | multi_voice_generator.py | compare_voices | ❌ |
| /api/multi-voice-generator/export | multi_voice_generator.py | export_multi_voice | ❌ |
| /api/multi-voice-generator/import | multi_voice_generator.py | import_multi_voice | ❌ |
| /api/multilingual/synthesize | multilingual.py | synthesize_multilingual | ❌ |
| /api/multilingual/translate | multilingual.py | translate_text | ❌ |
| /api/nr/apply | nr.py | apply | ❌ |
| /api/nr/noise-print/create | nr.py | create_noise_print | ❌ |
| /api/plugins/{plugin_id}/load | plugins.py | load_plugin | ❌ |
| /api/plugins/{plugin_id}/unload | plugins.py | unload_plugin | ❌ |
| /api/presets/ | presets.py | create_preset | ❌ |
| /api/presets/{preset_id}/apply | presets.py | apply_preset | ❌ |
| /api/profiles/{profile_id}/preprocess-reference | profiles.py | preprocess_reference_audio | ❌ |
| /api/projects/{project_id}/audio/save | projects.py | save_audio_to_project | ✅ |
| /api/prosody/apply | prosody.py | apply_prosody | ❌ |
| /api/prosody/configs | prosody.py | create_prosody_config | ❌ |
| /api/prosody/phonemes/analyze | prosody.py | analyze_phonemes | ❌ |
| /api/quality-pipelines/engines/{engine_id}/apply | quality_pipelines.py | apply_pipeline | ❌ |
| /api/quality-pipelines/engines/{engine_id}/compare | quality_pipelines.py | compare_pipeline | ❌ |
| /api/quality-pipelines/engines/{engine_id}/preview | quality_pipelines.py | preview_pipeline | ❌ |
| /api/quality/analyze | quality.py | analyze_quality | ❌ |
| /api/quality/analyze-text | quality.py | analyze_text_endpoint | ❌ |
| /api/quality/benchmark | quality.py | run_benchmark | ❌ |
| /api/quality/compare | quality.py | compare_quality | ❌ |
| /api/quality/consistency/record | quality.py | record_quality_metrics | ❌ |
| /api/quality/consistency/standard | quality.py | set_quality_standard | ❌ |
| /api/quality/history | quality.py | store_quality_history | ❌ |
| /api/quality/optimize | quality.py | optimize_quality | ❌ |
| /api/quality/recommend-quality | quality.py | recommend_quality_endpoint | ❌ |
| /api/quality/visualization/anomalies | quality.py | detect_quality_anomalies_endpoint | ❌ |
| /api/quality/visualization/correlations | quality.py | get_quality_correlations | ❌ |
| /api/quality/visualization/export/anomalies | quality.py | export_quality_anomalies | ❌ |
| /api/quality/visualization/export/correlations | quality.py | export_quality_correlations | ❌ |
| /api/quality/visualization/export/heatmap | quality.py | export_quality_heatmap | ❌ |
| /api/quality/visualization/export/insights | quality.py | export_quality_insights | ❌ |
| /api/quality/visualization/heatmap | quality.py | get_quality_heatmap | ❌ |
| /api/quality/visualization/insights | quality.py | get_quality_insights | ❌ |
| /api/quality/visualization/predict | quality.py | predict_quality_endpoint | ❌ |
| /api/realtime-converter/start | realtime_converter.py | start_converter_session | ❌ |
| /api/realtime-converter/{session_id}/pause | realtime_converter.py | pause_converter_session | ❌ |
| /api/realtime-converter/{session_id}/resume | realtime_converter.py | resume_converter_session | ❌ |
| /api/realtime-converter/{session_id}/stop | realtime_converter.py | stop_converter_session | ❌ |
| /api/realtime-visualizer/start | realtime_visualizer.py | start_visualizer_session | ❌ |
| /api/realtime-visualizer/{session_id}/stop | realtime_visualizer.py | stop_visualizer_session | ❌ |
| /api/recording/start | recording.py | start_recording | ❌ |
| /api/recording/{recording_id}/chunk | recording.py | append_audio_chunk | ❌ |
| /api/recording/{recording_id}/stop | recording.py | stop_recording | ❌ |
| /api/repair/clipping | repair.py | clipping | ❌ |
| /api/reward/predict | reward.py | predict | ❌ |
| /api/reward/train | reward.py | train | ❌ |
| /api/rvc/convert | rvc.py | convert_voice | ❌ |
| /api/rvc/models/upload | rvc.py | upload_model | ❌ |
| /api/rvc/start | rvc.py | start | ❌ |
| /api/rvc/stop | rvc.py | stop | ❌ |
| /api/safety/scan | safety.py | scan | ❌ |
| /api/scenes/{scene_id}/apply | scenes.py | apply_scene | ❌ |
| /api/scenes/{scene_id}/tracks | scenes.py | add_track_to_scene | ❌ |
| /api/script-editor/{script_id}/segments | script_editor.py | add_segment_to_script | ❌ |
| /api/script-editor/{script_id}/synthesize | script_editor.py | synthesize_script | ❌ |
| /api/settings/reset | settings.py | reset_settings | ❌ |
| /api/shortcuts/reset-all | shortcuts.py | reset_all_shortcuts | ❌ |
| /api/shortcuts/{shortcut_id}/reset | shortcuts.py | reset_shortcut | ❌ |
| /api/sonography/generate | sonography.py | generate_sonography | ❌ |
| /api/spatial-audio/apply | spatial_audio.py | apply_spatial_audio | ❌ |
| /api/spatial-audio/binaural | spatial_audio.py | generate_binaural_audio | ❌ |
| /api/spatial-audio/configs | spatial_audio.py | create_spatial_config | ❌ |
| /api/spatial-audio/environment | spatial_audio.py | configure_environment | ❌ |
| /api/spatial-audio/position | spatial_audio.py | set_voice_position | ❌ |
| /api/spatial-audio/preview | spatial_audio.py | preview_spatial_audio | ❌ |
| /api/spatial-audio/process | spatial_audio.py | process_spatial_audio | ❌ |
| /api/spectral/inpaint | spectral.py | inpaint | ❌ |
| /api/ssml/preview | ssml.py | preview_ssml | ❌ |
| /api/ssml/validate | ssml.py | validate_ssml | ❌ |
| /api/style-transfer/presets | style_transfer.py | create_style_preset | ❌ |
| /api/style-transfer/style/analyze | style_transfer.py | analyze_style | ❌ |
| /api/style-transfer/style/extract | style_transfer.py | extract_style | ❌ |
| /api/style-transfer/synthesize/style | style_transfer.py | synthesize_with_style | ❌ |
| /api/style-transfer/transfer | style_transfer.py | create_style_transfer | ❌ |
| /api/tags/merge | tags.py | merge_tags | ❌ |
| /api/tags/{tag_id}/decrement-usage | tags.py | decrement_tag_usage | ❌ |
| /api/tags/{tag_id}/increment-usage | tags.py | increment_tag_usage | ❌ |
| /api/templates/{template_id}/apply | templates.py | apply_template | ❌ |
| /api/text-highlighting/sync | text_highlighting.py | sync_highlighting | ❌ |
| /api/text-speech-editor/align | text_speech_editor.py | align_transcript | ❌ |
| /api/text-speech-editor/apply | text_speech_editor.py | apply_edits | ❌ |
| /api/text-speech-editor/insert-text | text_speech_editor.py | insert_text | ❌ |
| /api/text-speech-editor/merge | text_speech_editor.py | merge_segments | ❌ |
| /api/text-speech-editor/remove-filler-words | text_speech_editor.py | remove_filler_words | ❌ |
| /api/text-speech-editor/replace-word | text_speech_editor.py | replace_word | ❌ |
| /api/text-speech-editor/session/create | text_speech_editor.py | create_edit_session | ❌ |
| /api/tracks/{track_id}/clips | tracks.py | create_clip | ✅ |
| /api/training/cancel/{training_id} | training.py | cancel_training | ❌ |
| /api/training/datasets | training.py | create_dataset | ❌ |
| /api/training/export | training.py | export_trained_model | ❌ |
| /api/training/import | training.py | import_trained_model | ❌ |
| /api/training/start | training.py | start_training | ❌ |
| /api/transcribe/ | transcribe.py | transcribe_audio | ❌ |
| /api/upscaling/upscale | upscaling.py | upscale_media | ❌ |
| /api/video-gen/generate | video_gen.py | generate_video | ❌ |
| /api/video-gen/temporal-consistency | video_gen.py | enhance_temporal_consistency | ❌ |
| /api/video-gen/upscale | video_gen.py | upscale_video | ❌ |
| /api/video-gen/voice/convert | video_gen.py | convert_voice | ❌ |
| /api/voice-cloning-wizard/start | voice_cloning_wizard.py | start_wizard | ❌ |
| /api/voice-cloning-wizard/validate-audio | voice_cloning_wizard.py | validate_audio | ❌ |
| /api/voice-cloning-wizard/{job_id}/finalize | voice_cloning_wizard.py | finalize_wizard | ❌ |
| /api/voice-cloning-wizard/{job_id}/process | voice_cloning_wizard.py | process_wizard | ❌ |
| /api/voice-morph/apply | voice_morph.py | apply_morph | ❌ |
| /api/voice-morph/configs | voice_morph.py | create_morph_config | ❌ |
| /api/voice-morph/voice/blend | voice_morph.py | blend_voices | ❌ |
| /api/voice-morph/voice/embedding | voice_morph.py | get_voice_embedding | ❌ |
| /api/voice-morph/voice/morph | voice_morph.py | morph_voice | ❌ |
| /api/voice-morph/voice/preview | voice_morph.py | preview_voice | ❌ |
| /api/voice-speech/phonemize | voice_speech.py | phonemize_text | ❌ |
| /api/voice-speech/recognize | voice_speech.py | recognize_speech | ❌ |
| /api/voice/ab-test | voice.py | ab_test | ❌ |
| /api/voice/analyze | voice.py | analyze | ❌ |
| /api/voice/clone | voice.py | clone | ❌ |
| /api/voice/post-process | voice.py | post_process_pipeline | ❌ |
| /api/voice/prosody-control | voice.py | prosody_control | ❌ |
| /api/voice/remove-artifacts | voice.py | remove_artifacts | ❌ |
| /api/voice/synthesize | voice.py | synthesize | ❌ |
| /api/voice/synthesize/cross-lingual | voice.py | synthesize_cross_lingual | ❌ |
| /api/voice/synthesize/multipass | voice.py | synthesize_multipass | ❌ |
| /api/voice/synthesize/style | voice.py | synthesize_with_style | ❌ |
| /api/workflows/{workflow_id}/execute | workflows.py | execute_workflow | ❌ |

### PUT (40 endpoints)

| Path | File | Function | Implementation |
|------|------|----------|----------------|
| /api/api-key-manager/{key_id} | api_key_manager.py | update_api_key | ❌ |
| /api/automation/{curve_id} | automation.py | update_automation_curve | ❌ |
| /api/effects/chains/{chain_id} | effects.py | update_effect_chain | ✅ |
| /api/emotion/preset/{preset_id} | emotion.py | update_preset | ❌ |
| /api/lexicon/lexicons/{lexicon_id} | lexicon.py | update_lexicon | ❌ |
| /api/lexicon/lexicons/{lexicon_id}/entries/{word} | lexicon.py | update_lexicon_entry | ❌ |
| /api/lexicon/update | lexicon.py | update_lexicon_entry | ❌ |
| /api/library/assets/{asset_id} | library.py | update_asset | ❌ |
| /api/macros/automation/curves/{curve_id} | macros.py | update_automation_curve | ✅ |
| /api/macros/{macro_id} | macros.py | update_macro | ✅ |
| /api/markers/{marker_id} | markers.py | update_marker | ❌ |
| /api/mcp-dashboard/servers/{server_id} | mcp_dashboard.py | update_mcp_server | ❌ |
| /api/mixer/presets/{project_id}/{preset_id} | mixer.py | update_preset | ❌ |
| /api/mixer/state/{project_id} | mixer.py | update_mixer_state | ❌ |
| /api/mixer/state/{project_id}/master | mixer.py | update_master | ❌ |
| /api/mixer/state/{project_id}/returns/{return_id} | mixer.py | update_return | ❌ |
| /api/mixer/state/{project_id}/sends/{send_id} | mixer.py | update_send | ❌ |
| /api/mixer/state/{project_id}/subgroups/{subgroup_id} | mixer.py | update_subgroup | ❌ |
| /api/models/{engine}/{model_name}/update-checksum | models.py | update_model_checksum | ❌ |
| /api/plugins/{plugin_id}/config | plugins.py | update_plugin_config | ❌ |
| /api/presets/{preset_id} | presets.py | update_preset | ❌ |
| /api/profiles/{profile_id} | profiles.py | update_profile | ✅ |
| /api/projects/{project_id} | projects.py | update_project | ✅ |
| /api/prosody/configs/{config_id} | prosody.py | update_prosody_config | ❌ |
| /api/scenes/{scene_id} | scenes.py | update_scene | ❌ |
| /api/script-editor/{script_id} | script_editor.py | update_script | ❌ |
| /api/settings/{category} | settings.py | update_settings_category | ❌ |
| /api/shortcuts/{shortcut_id} | shortcuts.py | update_shortcut | ❌ |
| /api/spatial-audio/configs/{config_id} | spatial_audio.py | update_spatial_config | ❌ |
| /api/spectrogram/config/{audio_id} | spectrogram.py | update_spectrogram_config | ❌ |
| /api/ssml/{document_id} | ssml.py | update_ssml_document | ❌ |
| /api/tags/{tag_id} | tags.py | update_tag | ❌ |
| /api/templates/{template_id} | templates.py | update_template | ❌ |
| /api/text-highlighting/{session_id} | text_highlighting.py | update_highlighting_session | ❌ |
| /api/todo-panel/{todo_id} | todo_panel.py | update_todo | ❌ |
| /api/tracks/{track_id} | tracks.py | update_track | ✅ |
| /api/tracks/{track_id}/clips/{clip_id} | tracks.py | update_clip | ✅ |
| /api/voice-morph/configs/{config_id} | voice_morph.py | update_morph_config | ❌ |
| /api/waveform/config/{audio_id} | waveform.py | update_waveform_config | ❌ |
| /api/workflows/{workflow_id} | workflows.py | update_workflow | ❌ |

---

## 📁 Route Files Analysis

| File | Endpoints | Violations | Structure Issues |
|------|-----------|------------|------------------|
| adr.py | 1 | 0 | ⚠️ 1 |
| advanced_settings.py | 2 | 0 | ✅ |
| advanced_spectrogram.py | 6 | 1 | ✅ |
| ai_production_assistant.py | 5 | 0 | ✅ |
| analytics.py | 7 | 4 | ✅ |
| api_key_manager.py | 5 | 0 | ✅ |
| articulation.py | 1 | 0 | ⚠️ 1 |
| assistant.py | 5 | 0 | ✅ |
| assistant_run.py | 3 | 0 | ⚠️ 1 |
| audio.py | 6 | 0 | ✅ |
| audio_analysis.py | 6 | 0 | ✅ |
| audio_audit.py | 4 | 0 | ⚠️ 1 |
| auth.py | 6 | 0 | ✅ |
| automation.py | 6 | 0 | ✅ |
| backup.py | 5 | 6 | ✅ |
| batch.py | 11 | 1 | ✅ |
| dataset.py | 5 | 0 | ✅ |
| dataset_editor.py | 3 | 0 | ✅ |
| deepfake_creator.py | 6 | 6 | ✅ |
| docs.py | 3 | 0 | ⚠️ 1 |
| dubbing.py | 2 | 0 | ⚠️ 1 |
| effects.py | 9 | 0 | ✅ |
| embedding_explorer.py | 7 | 1 | ✅ |
| emotion.py | 9 | 0 | ✅ |
| emotion_style.py | 3 | 0 | ✅ |
| engine.py | 3 | 0 | ⚠️ 1 |
| engine_audit.py | 4 | 0 | ⚠️ 1 |
| engines.py | 3 | 0 | ✅ |
| ensemble.py | 4 | 0 | ✅ |
| eval_abx.py | 5 | 0 | ✅ |
| formant.py | 2 | 0 | ⚠️ 1 |
| gpu_status.py | 2 | 1 | ✅ |
| granular.py | 1 | 0 | ⚠️ 1 |
| health.py | 9 | 0 | ⚠️ 1 |
| help.py | 6 | 0 | ✅ |
| huggingface_fix.py | 0 | 0 | ⚠️ 3 |
| image_gen.py | 5 | 2 | ✅ |
| image_search.py | 6 | 0 | ✅ |
| img_sampler.py | 3 | 1 | ⚠️ 1 |
| jobs.py | 6 | 0 | ✅ |
| lexicon.py | 15 | 0 | ✅ |
| library.py | 8 | 0 | ✅ |
| macros.py | 12 | 0 | ✅ |
| markers.py | 4 | 0 | ✅ |
| mcp_dashboard.py | 7 | 1 | ✅ |
| mix_assistant.py | 11 | 0 | ✅ |
| mix_scene.py | 1 | 0 | ⚠️ 1 |
| mixer.py | 21 | 0 | ✅ |
| ml_optimization.py | 3 | 2 | ✅ |
| model_inspect.py | 2 | 4 | ⚠️ 1 |
| models.py | 8 | 1 | ✅ |
| monitoring.py | 9 | 0 | ⚠️ 1 |
| multi_voice_generator.py | 5 | 0 | ✅ |
| multilingual.py | 5 | 0 | ✅ |
| nr.py | 3 | 0 | ⚠️ 1 |
| plugins.py | 6 | 2 | ✅ |
| presets.py | 8 | 0 | ✅ |
| profiles.py | 4 | 0 | ✅ |
| projects.py | 6 | 0 | ✅ |
| prosody.py | 7 | 0 | ✅ |
| quality.py | 29 | 1 | ✅ |
| quality_pipelines.py | 4 | 1 | ✅ |
| realtime_converter.py | 6 | 1 | ✅ |
| realtime_visualizer.py | 4 | 0 | ✅ |
| recording.py | 6 | 0 | ✅ |
| repair.py | 1 | 0 | ⚠️ 1 |
| reward.py | 4 | 1 | ⚠️ 1 |
| rvc.py | 6 | 1 | ⚠️ 1 |
| safety.py | 2 | 0 | ⚠️ 1 |
| scenes.py | 6 | 0 | ✅ |
| script_editor.py | 6 | 1 | ✅ |
| search.py | 0 | 0 | ✅ |
| settings.py | 3 | 1 | ✅ |
| shortcuts.py | 7 | 0 | ✅ |
| sonography.py | 4 | 0 | ✅ |
| spatial_audio.py | 11 | 1 | ✅ |
| spectral.py | 1 | 0 | ⚠️ 1 |
| spectrogram.py | 6 | 1 | ✅ |
| ssml.py | 5 | 0 | ✅ |
| style_transfer.py | 9 | 0 | ✅ |
| tags.py | 8 | 0 | ✅ |
| templates.py | 5 | 0 | ✅ |
| text_highlighting.py | 4 | 0 | ✅ |
| text_speech_editor.py | 8 | 1 | ✅ |
| todo_panel.py | 7 | 2 | ✅ |
| tracks.py | 6 | 0 | ✅ |
| training.py | 12 | 0 | ✅ |
| training_audit.py | 4 | 0 | ⚠️ 1 |
| transcribe.py | 5 | 0 | ✅ |
| ultimate_dashboard.py | 4 | 0 | ✅ |
| upscaling.py | 6 | 0 | ✅ |
| video_edit.py | 1 | 0 | ✅ |
| video_gen.py | 6 | 1 | ✅ |
| voice.py | 11 | 0 | ✅ |
| voice_browser.py | 4 | 0 | ✅ |
| voice_cloning_wizard.py | 6 | 0 | ✅ |
| voice_morph.py | 10 | 1 | ✅ |
| voice_speech.py | 4 | 0 | ✅ |
| waveform.py | 5 | 0 | ✅ |
| workflows.py | 4 | 1 | ✅ |

---

## 🔍 Detailed Route File Status

### adr.py

- **Endpoints:** 1
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### advanced_settings.py

- **Endpoints:** 2
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### advanced_spectrogram.py

- **Endpoints:** 6
- **Code Quality:** ⚠️ 1 violations found
  - Line 208: Found 'temporary' - # Save to temporary file
- **Structure:** ✅ No issues

### ai_production_assistant.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### analytics.py

- **Endpoints:** 7
- **Code Quality:** ⚠️ 4 violations found
  - Line 710: Found 'dummy' - # Create a dummy model for yellowbrick
  - Line 744: Found 'dummy' - # Create a dummy model for yellowbrick
  - Line 783: Found 'dummy' - # Create a dummy classifier for yellowbrick
  - Line 837: Found 'temporary' - # Save to temporary file
- **Structure:** ✅ No issues

### api_key_manager.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### articulation.py

- **Endpoints:** 1
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### assistant.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### assistant_run.py

- **Endpoints:** 3
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### audio.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### audio_analysis.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### audio_audit.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### auth.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### automation.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### backup.py

- **Endpoints:** 5
- **Code Quality:** ⚠️ 6 violations found
  - Line 22: Found 'not yet' - # Logger not yet defined, will log later if needed
  - Line 22: Found 'later' - # Logger not yet defined, will log later if needed
  - Line 230: Found 'temporary' - # Create temporary directory for backup contents
  - Line 373: Found 'temporary' - # Clean up temporary directory
  - Line 423: Found 'temporary' - # Create temporary directory for extraction
- **Structure:** ✅ No issues

### batch.py

- **Endpoints:** 11
- **Code Quality:** ⚠️ 1 violations found
  - Line 677: Found 'temporary' - # Use temporary file or project directory
- **Structure:** ✅ No issues

### dataset.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### dataset_editor.py

- **Endpoints:** 3
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### deepfake_creator.py

- **Endpoints:** 6
- **Code Quality:** ⚠️ 6 violations found
  - Line 17: Found 'fake' - # In-memory storage for deepfake jobs (replace with database in production)
  - Line 85: Found 'fake' - # Validate consent (required for deepfake creation)
  - Line 303: Found 'fake' - # Try to use deepfake engine
  - Line 319: Found 'fake' - # Process deepfake
  - Line 323: Found 'fake' - # Process image deepfake
- **Structure:** ✅ No issues

### docs.py

- **Endpoints:** 3
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### dubbing.py

- **Endpoints:** 2
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### effects.py

- **Endpoints:** 9
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### embedding_explorer.py

- **Endpoints:** 7
- **Code Quality:** ⚠️ 1 violations found
  - Line 93: Found 'later' - # 5. Store embedding for later use
- **Structure:** ✅ No issues

### emotion.py

- **Endpoints:** 9
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### emotion_style.py

- **Endpoints:** 3
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### engine.py

- **Endpoints:** 3
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### engine_audit.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### engines.py

- **Endpoints:** 3
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### ensemble.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### eval_abx.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### formant.py

- **Endpoints:** 2
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### gpu_status.py

- **Endpoints:** 2
- **Code Quality:** ⚠️ 1 violations found
  - Line 62: Found 'not yet' - # 2. pyamdgpuinfo for AMD GPUs (not yet implemented)
- **Structure:** ✅ No issues

### granular.py

- **Endpoints:** 1
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### health.py

- **Endpoints:** 9
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### help.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### huggingface_fix.py

- **Endpoints:** 0
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No APIRouter definition found
  - FastAPI imports may be missing
  - No response_model parameters found (may be intentional)

### image_gen.py

- **Endpoints:** 5
- **Code Quality:** ⚠️ 2 violations found
  - Line 311: Found 'temporary' - # Create temporary output file
  - Line 605: Found 'not yet' - # Return error indicating video processing not yet implemented
- **Structure:** ✅ No issues

### image_search.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### img_sampler.py

- **Endpoints:** 3
- **Code Quality:** ⚠️ 1 violations found
  - Line 178: Found 'PLACEHOLDER' - # Create a simple placeholder image
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### jobs.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### lexicon.py

- **Endpoints:** 15
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### library.py

- **Endpoints:** 8
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### macros.py

- **Endpoints:** 12
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### markers.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### mcp_dashboard.py

- **Endpoints:** 7
- **Code Quality:** ⚠️ 1 violations found
  - Line 314: Found 'for now' - # to the MCP server. For now, simulate connection.
- **Structure:** ✅ No issues

### mix_assistant.py

- **Endpoints:** 11
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### mix_scene.py

- **Endpoints:** 1
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### mixer.py

- **Endpoints:** 21
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### ml_optimization.py

- **Endpoints:** 3
- **Code Quality:** ⚠️ 2 violations found
  - Line 106: Found 'for now' - # For now, return a message indicating it needs custom implementation
  - Line 170: Found 'dummy' - # Fit on dummy data for demo
- **Structure:** ✅ No issues

### model_inspect.py

- **Endpoints:** 2
- **Code Quality:** ⚠️ 4 violations found
  - Line 117: Found 'dummy' - # Create dummy input for activation extraction
  - Line 119: Found 'for now' - # For now, create a simple feature map
  - Line 134: Found 'dummy' - # Forward pass with dummy input
  - Line 136: Found 'dummy' - # Create appropriate dummy input based on model type
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### models.py

- **Endpoints:** 8
- **Code Quality:** ⚠️ 1 violations found
  - Line 250: Found 'temporary' - # Create temporary ZIP file
- **Structure:** ✅ No issues

### monitoring.py

- **Endpoints:** 9
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### multi_voice_generator.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### multilingual.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### nr.py

- **Endpoints:** 3
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### plugins.py

- **Endpoints:** 6
- **Code Quality:** ⚠️ 2 violations found
  - Line 360: Found 'for now' - # For now, return a message indicating the plugin would be loaded
  - Line 414: Found 'for now' - # For now, return a message indicating the plugin would be unloaded
- **Structure:** ✅ No issues

### presets.py

- **Endpoints:** 8
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### profiles.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### projects.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### prosody.py

- **Endpoints:** 7
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### quality.py

- **Endpoints:** 29
- **Code Quality:** ⚠️ 1 violations found
  - Line 419: Found 'temporary' - # Save to temporary file
- **Structure:** ✅ No issues

### quality_pipelines.py

- **Endpoints:** 4
- **Code Quality:** ⚠️ 1 violations found
  - Line 167: Found 'temporary' - # Save to temporary location
- **Structure:** ✅ No issues

### realtime_converter.py

- **Endpoints:** 6
- **Code Quality:** ⚠️ 1 violations found
  - Line 222: Found 'temporary' - # Save chunk to temporary file for RVC processing
- **Structure:** ✅ No issues

### realtime_visualizer.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### recording.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### repair.py

- **Endpoints:** 1
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### reward.py

- **Endpoints:** 4
- **Code Quality:** ⚠️ 1 violations found
  - Line 184: Found 'for now' - # For now, use model mean as baseline
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### rvc.py

- **Endpoints:** 6
- **Code Quality:** ⚠️ 1 violations found
  - Line 486: Found 'for now' - # For now, just return success
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### safety.py

- **Endpoints:** 2
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### scenes.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### script_editor.py

- **Endpoints:** 6
- **Code Quality:** ⚠️ 1 violations found
  - Line 521: Found 'temporary' - # Save segment to temporary file
- **Structure:** ✅ No issues

### search.py

- **Endpoints:** 0
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### settings.py

- **Endpoints:** 3
- **Code Quality:** ⚠️ 1 violations found
  - Line 292: Found 'temporary' - # Save settings atomically using a temporary file
- **Structure:** ✅ No issues

### shortcuts.py

- **Endpoints:** 7
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### sonography.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### spatial_audio.py

- **Endpoints:** 11
- **Code Quality:** ⚠️ 1 violations found
  - Line 597: Found 'temporary' - # Create temporary config and apply
- **Structure:** ✅ No issues

### spectral.py

- **Endpoints:** 1
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### spectrogram.py

- **Endpoints:** 6
- **Code Quality:** ⚠️ 1 violations found
  - Line 556: Found 'temporary' - # Save to temporary file
- **Structure:** ✅ No issues

### ssml.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### style_transfer.py

- **Endpoints:** 9
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### tags.py

- **Endpoints:** 8
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### templates.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### text_highlighting.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### text_speech_editor.py

- **Endpoints:** 8
- **Code Quality:** ⚠️ 1 violations found
  - Line 838: Found 'for now' - # For now, we'll use original audio for segments that weren't edited
- **Structure:** ✅ No issues

### todo_panel.py

- **Endpoints:** 7
- **Code Quality:** ⚠️ 2 violations found
  - Line 94: Found 'TODO' - # Create todos table
  - Line 132: Found 'TODO' - # Create todos table
- **Structure:** ✅ No issues

### tracks.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### training.py

- **Endpoints:** 12
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### training_audit.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ⚠️ Issues found
  - No response_model parameters found (may be intentional)

### transcribe.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### ultimate_dashboard.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### upscaling.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### video_edit.py

- **Endpoints:** 1
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### video_gen.py

- **Endpoints:** 6
- **Code Quality:** ⚠️ 1 violations found
  - Line 140: Found 'temporary' - # Create temporary output file
- **Structure:** ✅ No issues

### voice.py

- **Endpoints:** 11
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### voice_browser.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### voice_cloning_wizard.py

- **Endpoints:** 6
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### voice_morph.py

- **Endpoints:** 10
- **Code Quality:** ⚠️ 1 violations found
  - Line 747: Found 'PLACEHOLDER' - # If all extraction methods failed, return error instead of placeholder
- **Structure:** ✅ No issues

### voice_speech.py

- **Endpoints:** 4
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### waveform.py

- **Endpoints:** 5
- **Code Quality:** ✅ No violations
- **Structure:** ✅ No issues

### workflows.py

- **Endpoints:** 4
- **Code Quality:** ⚠️ 1 violations found
  - Line 692: Found 'for now' - # For now, just normalize (proper filter would require scipy)
- **Structure:** ✅ No issues


---

## 📝 Notes

- ✅ = Success
- ❌ = Failed or Not Available
- ⚠️ = Warning or Issue Found
- Code quality violations include TODO, FIXME, placeholders, etc.
- Implementation checks verify functions are not just 'pass' or raise NotImplementedError
