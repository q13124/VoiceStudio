# Quality Features API Quick Reference
## VoiceStudio Quantum+ - Quality Improvement Features

Quick reference guide for all quality improvement API endpoints (IDEA 61-70).

---

## Quick Endpoint Reference

### Voice Quality Enhancement

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|----------------|
| `/api/voice/synthesize/multipass` | POST | Multi-pass synthesis with quality refinement | `max_passes`, `pass_preset`, `adaptive` |
| `/api/voice/remove-artifacts` | POST | Detect and remove audio artifacts | `artifact_types`, `repair_preset`, `preview` |
| `/api/voice/analyze-characteristics` | POST | Analyze voice characteristics | `audio_id`, `reference_audio_id`, `include_prosody` |
| `/api/voice/prosody-control` | POST | Control prosody and intonation | `intonation_pattern`, `pitch_contour`, `stress_markers` |
| `/api/voice/post-process` | POST | Multi-stage post-processing pipeline | `enhancement_stages`, `optimize_order`, `preview` |

### Reference Audio Optimization

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|----------------|
| `/api/profiles/{profile_id}/preprocess-reference` | POST | Pre-process reference audio for cloning | `auto_enhance`, `select_optimal_segments`, `max_segments` |

### Image/Video Quality Enhancement

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|----------------|
| `/api/image/enhance-face` | POST | Enhance face quality in images/videos | `image_id`/`video_id`, `enhancement_preset`, `multi_stage` |
| `/api/video/temporal-consistency` | POST | Enhance temporal consistency for videos | `video_id`, `smoothing_strength`, `detect_artifacts` |

### Training Data Optimization

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|----------------|
| `/api/training/datasets/{dataset_id}/optimize` | POST | Optimize training data quality | `analyze_quality`, `select_optimal`, `suggest_augmentation` |

---

## Decision Tree: When to Use Each Feature

```
Start: I want to improve quality

├─ Voice Synthesis Quality?
│  ├─ Need highest quality synthesis?
│  │  └─ Use: Multi-Pass Synthesis (/api/voice/synthesize/multipass)
│  │     └─ Presets: naturalness_focus, similarity_focus, artifact_focus
│  │
│  ├─ Audio has clicks/pops/distortion?
│  │  └─ Use: Artifact Removal (/api/voice/remove-artifacts)
│  │     └─ Types: clicks, pops, distortion, glitches, phase_issues
│  │
│  ├─ Need to preserve voice characteristics?
│  │  └─ Use: Voice Characteristic Analysis (/api/voice/analyze-characteristics)
│  │     └─ Compare with reference_audio_id
│  │
│  ├─ Need better intonation/prosody?
│  │  └─ Use: Prosody Control (/api/voice/prosody-control)
│  │     └─ Patterns: rising, falling, flat
│  │
│  └─ Need comprehensive enhancement?
│     └─ Use: Post-Processing Pipeline (/api/voice/post-process)
│        └─ Stages: denoise, normalize, enhance, repair

├─ Reference Audio Quality?
│  └─ Use: Reference Audio Pre-Processing (/api/profiles/{profile_id}/preprocess-reference)
│     └─ Auto-enhance and select optimal segments

├─ Image/Video Quality?
│  ├─ Face quality issues in image/video?
│  │  └─ Use: Face Enhancement (/api/image/enhance-face)
│  │     └─ Presets: portrait, full_body, close_up
│  │
│  └─ Video has flickering/jitter?
│     └─ Use: Temporal Consistency (/api/video/temporal-consistency)
│        └─ Adjust smoothing_strength (0.0-1.0)

└─ Training Data Quality?
   └─ Use: Training Data Optimization (/api/training/datasets/{dataset_id}/optimize)
      └─ Analyze quality, diversity, and select optimal samples
```

---

## Endpoint Comparison Table

### Voice Quality Endpoints

| Feature | Use Case | Processing Time | Quality Impact | Best For |
|---------|----------|----------------|----------------|----------|
| **Multi-Pass Synthesis** | Generate highest quality synthesis | High (3-10 passes) | Very High | Final production audio |
| **Artifact Removal** | Fix clicks/pops/distortion | Medium | High | Post-synthesis cleanup |
| **Voice Characteristics** | Preserve voice identity | Low (analysis only) | Medium | Pre-synthesis validation |
| **Prosody Control** | Improve intonation | Low | Medium | Emotional/natural speech |
| **Post-Processing** | Comprehensive enhancement | Medium-High | High | Final polish |

### Image/Video Quality Endpoints

| Feature | Use Case | Processing Time | Quality Impact | Best For |
|---------|----------|----------------|----------------|----------|
| **Face Enhancement** | Improve face quality | Medium | High | Portrait/close-up images |
| **Temporal Consistency** | Fix video flickering | High | Very High | Video deepfakes |

### Reference & Training Endpoints

| Feature | Use Case | Processing Time | Quality Impact | Best For |
|---------|----------|----------------|----------------|----------|
| **Reference Pre-Processing** | Optimize reference audio | Low | High | Before voice cloning |
| **Training Data Optimization** | Improve training data | Medium | Very High | Before model training |

---

## Recommended Workflows

### Workflow 1: High-Quality Voice Synthesis

```
1. Pre-process reference audio
   POST /api/profiles/{profile_id}/preprocess-reference
   
2. Multi-pass synthesis
   POST /api/voice/synthesize/multipass
   (pass_preset: "naturalness_focus")
   
3. Remove artifacts
   POST /api/voice/remove-artifacts
   
4. Post-processing pipeline
   POST /api/voice/post-process
   (stages: ["denoise", "normalize", "enhance"])
```

### Workflow 2: Voice Cloning with Preservation

```
1. Analyze reference characteristics
   POST /api/voice/analyze-characteristics
   (reference_audio_id)
   
2. Synthesize with multi-pass
   POST /api/voice/synthesize/multipass
   
3. Verify characteristics preserved
   POST /api/voice/analyze-characteristics
   (compare with reference)
   
4. Apply prosody control if needed
   POST /api/voice/prosody-control
```

### Workflow 3: Video Deepfake Enhancement

```
1. Generate video
   POST /api/video/generate
   
2. Enhance face quality
   POST /api/image/enhance-face
   (video_id, enhancement_preset: "portrait")
   
3. Improve temporal consistency
   POST /api/video/temporal-consistency
   (smoothing_strength: 0.6)
```

### Workflow 4: Training Data Preparation

```
1. Analyze training dataset
   POST /api/training/datasets/{dataset_id}/optimize
   (analyze_quality: true, analyze_diversity: true)
   
2. Use optimized dataset
   (Use optimized_dataset_id for training)
```

---

## Quick Parameter Reference

### Multi-Pass Synthesis

- **`max_passes`**: 1-10 (default: 3)
- **`pass_preset`**: `"naturalness_focus"`, `"similarity_focus"`, `"artifact_focus"`
- **`adaptive`**: `true` (stops early if improvement minimal)

### Artifact Removal

- **`artifact_types`**: `["clicks", "pops", "distortion", "glitches", "phase_issues"]`
- **`repair_preset`**: `"click_removal"`, `"distortion_repair"`, `"comprehensive"`
- **`preview`**: `true` (analyze only, don't repair)

### Prosody Control

- **`intonation_pattern`**: `"rising"`, `"falling"`, `"flat"`
- **`pitch_contour`**: Array of pitch values (Hz)
- **`stress_markers`**: Array of word stress markers

### Post-Processing

- **`enhancement_stages`**: `["denoise", "normalize", "enhance", "repair"]`
- **`optimize_order`**: `true` (auto-optimize stage order)
- **`preview`**: `true` (preview without applying)

### Face Enhancement

- **`enhancement_preset`**: `"portrait"`, `"full_body"`, `"close_up"`
- **`multi_stage`**: `true` (apply multi-stage enhancement)
- **`face_specific`**: `true` (face-specific enhancement)

### Temporal Consistency

- **`smoothing_strength`**: 0.0-1.0 (default: 0.5)
- **`motion_consistency`**: `true` (ensure motion consistency)
- **`detect_artifacts`**: `true` (detect temporal artifacts)

---

## Quality Score Interpretation

### Quality Score Ranges (0.0-1.0)

- **0.0-0.5**: Poor quality, significant improvement needed
- **0.5-0.7**: Acceptable quality, minor improvements recommended
- **0.7-0.85**: Good quality, suitable for most use cases
- **0.85-0.95**: Excellent quality, production-ready
- **0.95-1.0**: Near-perfect quality, maximum fidelity

### MOS Score Ranges (1.0-5.0)

- **1.0-2.0**: Poor quality, not recommended
- **2.0-3.0**: Fair quality, acceptable for testing
- **3.0-4.0**: Good quality, suitable for general use
- **4.0-4.5**: Very good quality, production-ready
- **4.5-5.0**: Excellent quality, near-perfect

### Similarity Score Ranges (0.0-1.0)

- **0.0-0.6**: Low similarity, voice doesn't match reference
- **0.6-0.75**: Moderate similarity, noticeable differences
- **0.75-0.85**: Good similarity, minor differences
- **0.85-0.95**: High similarity, very close match
- **0.95-1.0**: Near-perfect similarity, indistinguishable

---

## Common Use Cases

### Use Case 1: Quick Quality Check

```python
# Check quality without processing
result = remove_artifacts(audio_id, preview=True)
if result['artifacts_detected']:
    # Apply repair
    repair_result = remove_artifacts(audio_id, preview=False)
```

### Use Case 2: Maximum Quality Production

```python
# 1. Pre-process reference
preprocess_reference_audio(profile_id)

# 2. Multi-pass synthesis
multipass_result = synthesize_multipass(
    profile_id, text, max_passes=5, 
    pass_preset="naturalness_focus"
)

# 3. Remove artifacts
remove_artifacts(multipass_result['audio_id'])

# 4. Post-processing
post_process_audio(multipass_result['audio_id'])
```

### Use Case 3: Voice Characteristic Validation

```python
# Analyze before synthesis
ref_analysis = analyze_voice_characteristics(reference_audio_id)

# Synthesize
synthesis_result = synthesize(profile_id, text)

# Verify preservation
synth_analysis = analyze_voice_characteristics(
    synthesis_result['audio_id'], 
    reference_audio_id
)

if synth_analysis['similarity_score'] < 0.8:
    # Adjust synthesis parameters
    pass
```

---

## Performance Considerations

### Processing Time Estimates

- **Multi-Pass Synthesis**: 3-10x normal synthesis time (depends on `max_passes`)
- **Artifact Removal**: +10-30% processing time
- **Voice Characteristics**: +5-10% processing time (analysis only)
- **Prosody Control**: +5-15% processing time
- **Post-Processing**: +20-50% processing time (depends on stages)
- **Face Enhancement**: +30-60% processing time (images), +100-200% (videos)
- **Temporal Consistency**: +50-100% processing time
- **Reference Pre-Processing**: +5-15% processing time
- **Training Data Optimization**: +10-20% per sample analyzed

### Memory Usage

- Most quality features: Low-Moderate memory usage
- Multi-Pass Synthesis: High memory (stores multiple passes)
- Post-Processing: Moderate-High memory (temporary buffers)
- Temporal Consistency: High memory (frame buffers)

---

## Best Practices

1. **Use Preview Mode First**: Always preview artifacts/post-processing before applying
2. **Adaptive Multi-Pass**: Enable `adaptive=true` to save time on good quality passes
3. **Combine Features Wisely**: Don't apply all features - use based on actual needs
4. **Check Quality Scores**: Monitor quality metrics to determine if features are effective
5. **Optimize Workflow Order**: Pre-process reference → Synthesize → Post-process → Verify
6. **Batch Processing**: Use batch endpoints for multiple files to reduce overhead
7. **WebSocket Quality Updates**: Subscribe to `quality` topic for real-time monitoring

---

## Troubleshooting

### Low Quality Improvement

- **Check input quality**: Quality features work best with good input
- **Adjust parameters**: Try different presets or parameter values
- **Verify engine compatibility**: Some features work better with specific engines
- **Check logs**: Review backend logs for warnings or errors

### High Processing Time

- **Reduce `max_passes`**: Use 3-5 passes instead of 10
- **Skip unnecessary stages**: Only use needed post-processing stages
- **Use preview mode**: Preview before full processing
- **Enable adaptive stopping**: Let multi-pass stop early if quality plateaus

### Artifacts Not Removed

- **Specify artifact types**: Be explicit about which artifacts to check
- **Use comprehensive preset**: Try `"comprehensive"` repair preset
- **Check severity**: Low-severity artifacts may not be removed
- **Try multiple passes**: Some artifacts require multiple removal passes

---

## Related Documentation

- [Complete Endpoints List](ENDPOINTS.md#quality-improvement-features)
- [API Reference](API_REFERENCE.md#quality-improvement-features)
- [Code Examples](EXAMPLES.md#quality-improvement-features)
- [WebSocket Quality Preview](WEBSOCKET_EVENTS.md#quality-preview)

---

**Quick Reference Version:** 1.0  
**Last Updated:** 2025-01-27

