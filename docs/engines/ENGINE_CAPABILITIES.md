# Engine Capabilities Reference

Complete capabilities matrix for all engines.

## Capabilities Overview

Engines support various capabilities:
- **Synthesis:** Text-to-speech generation
- **Cloning:** Voice cloning from reference
- **Conversion:** Voice conversion
- **Transcription:** Speech-to-text
- **Batch Processing:** Multiple items at once
- **Streaming:** Real-time processing
- **Multilingual:** Multiple language support
- **Quality Metrics:** Built-in quality assessment

---

## Audio Engine Capabilities

### Text-to-Speech Engines

| Engine | Synthesis | Cloning | Batch | Streaming | Multilingual | Quality Metrics |
|--------|-----------|---------|-------|-----------|--------------|-----------------|
| XTTS v2 | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| Chatterbox | ✅ | ⚠️ | ⚠️ | ❌ | ⚠️ | ⚠️ |
| Tortoise | ✅ | ✅ | ❌ | ❌ | ⚠️ | ⚠️ |
| OpenVoice | ✅ | ✅ | ⚠️ | ❌ | ✅ | ⚠️ |
| Piper | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| F5 TTS | ✅ | ⚠️ | ⚠️ | ❌ | ⚠️ | ⚠️ |
| OpenAI TTS | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| Silero | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| ESpeak-NG | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| Festival/Flite | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| MaryTTS | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| RHVoice | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| Parakeet | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ |
| GPT-SoVITS | ✅ | ✅ | ⚠️ | ❌ | ⚠️ | ⚠️ |
| MockingBird | ✅ | ✅ | ⚠️ | ❌ | ⚠️ | ⚠️ |
| Lyrebird | ✅ | ✅ | ⚠️ | ❌ | ⚠️ | ⚠️ |
| Voice.ai | ✅ | ✅ | ⚠️ | ❌ | ⚠️ | ⚠️ |

**Legend:**
- ✅ Full support
- ⚠️ Partial support
- ❌ Not supported

### Voice Conversion Engines

| Engine | Conversion | Real-time | Batch | Pitch Shift | Formant Shift |
|--------|------------|-----------|-------|-------------|---------------|
| RVC | ✅ | ✅ | ❌ | ✅ | ✅ |
| VoxCPM | ✅ | ⚠️ | ❌ | ⚠️ | ⚠️ |
| OpenVoice | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |

### Speech-to-Text Engines

| Engine | Transcription | Multilingual | Timestamps | Word-level | Real-time |
|--------|---------------|--------------|------------|------------|-----------|
| Whisper | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Whisper.cpp | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Whisper UI | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| Vosk | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |

---

## Image Engine Capabilities

### Image Generation Engines

| Engine | Text-to-Image | Image-to-Image | Inpainting | Upscaling | ControlNet |
|--------|---------------|----------------|------------|-----------|------------|
| SDXL | ✅ | ✅ | ✅ | ❌ | ✅ |
| SDXL ComfyUI | ✅ | ✅ | ✅ | ❌ | ✅ |
| Stable Diffusion | ✅ | ✅ | ✅ | ❌ | ✅ |
| Stable Diffusion Next | ✅ | ✅ | ✅ | ❌ | ✅ |
| FastSD CPU | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| OpenJourney | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| Realistic Vision | ✅ | ✅ | ✅ | ❌ | ✅ |
| InvokeAI | ✅ | ✅ | ✅ | ❌ | ✅ |
| Automatic1111 | ✅ | ✅ | ✅ | ❌ | ✅ |
| ComfyUI | ✅ | ✅ | ✅ | ❌ | ✅ |
| Fooocus | ✅ | ✅ | ✅ | ❌ | ✅ |
| LocalAI | ✅ | ⚠️ | ⚠️ | ❌ | ⚠️ |

### Image Enhancement Engines

| Engine | Upscaling | Face Enhancement | Denoising | Super-resolution |
|--------|-----------|-------------------|-----------|------------------|
| RealESRGAN | ✅ | ❌ | ✅ | ✅ |
| DeepFaceLab | ❌ | ✅ | ❌ | ❌ |

---

## Video Engine Capabilities

### Video Generation Engines

| Engine | Text-to-Video | Image-to-Video | Video-to-Video | Face Animation |
|--------|---------------|----------------|----------------|----------------|
| SVD | ✅ | ✅ | ❌ | ❌ |
| Deforum | ✅ | ✅ | ✅ | ❌ |
| FOMM | ❌ | ❌ | ❌ | ✅ |
| SadTalker | ❌ | ❌ | ❌ | ✅ |
| Video Creator | ✅ | ✅ | ✅ | ⚠️ |
| MoviePy | ❌ | ❌ | ✅ | ❌ |
| FFmpeg AI | ❌ | ❌ | ✅ | ❌ |

---

## Performance Characteristics

### Processing Speed

**Fast (< 1 second):**
- Piper
- ESpeak-NG
- Festival/Flite
- FastSD CPU

**Medium (1-5 seconds):**
- Chatterbox
- OpenVoice
- RVC
- Stable Diffusion

**Slow (> 5 seconds):**
- XTTS v2 (first use)
- Tortoise TTS
- SDXL
- SVD

### Memory Requirements

**Low (< 2GB VRAM):**
- Piper
- ESpeak-NG
- Festival/Flite
- FastSD CPU

**Medium (2-8GB VRAM):**
- Chatterbox
- OpenVoice
- RVC
- Stable Diffusion

**High (> 8GB VRAM):**
- XTTS v2
- Tortoise TTS
- SDXL
- SVD

---

## Quality Characteristics

### Voice Quality

**Best Quality:**
- XTTS v2
- Tortoise TTS
- GPT-SoVITS

**Good Quality:**
- Chatterbox
- OpenVoice
- RVC

**Basic Quality:**
- Piper
- ESpeak-NG
- Festival/Flite

### Image Quality

**Best Quality:**
- SDXL
- Realistic Vision
- ComfyUI

**Good Quality:**
- Stable Diffusion
- InvokeAI
- Automatic1111

**Basic Quality:**
- FastSD CPU
- OpenJourney

---

## Use Case Recommendations

### Voice Cloning
- **Best:** XTTS v2
- **Alternative:** Tortoise TTS, GPT-SoVITS

### Fast Synthesis
- **Best:** Piper, Chatterbox
- **Alternative:** ESpeak-NG, Festival/Flite

### Multilingual Support
- **Best:** XTTS v2, Whisper
- **Alternative:** OpenAI TTS, Silero

### Real-time Processing
- **Best:** RVC, Vosk
- **Alternative:** Streaming Engine

### High-Quality Images
- **Best:** SDXL, Realistic Vision
- **Alternative:** Stable Diffusion, ComfyUI

### Image Upscaling
- **Best:** RealESRGAN
- **Alternative:** SDXL (with upscaling)

---

**Last Updated:** 2025-01-28

