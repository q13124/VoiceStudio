# VoiceStudio Quantum+ Engine Recommendations

**Source:** Offline Voice Cloning, Synthesis, and Transcription Tools (2025)

## High-Priority Tools for VoiceStudio Quantum+

### Voice Cloning & TTS Engines

#### **Chatterbox TTS** (Resemble AI) - **PRIMARY RECOMMENDATION**
- **Quality:** State-of-the-art, outperforms ElevenLabs
- **Features:** Zero-shot voice cloning, multilingual (23 languages), expressive speech with emotion control
- **Install:** `pip install chatterbox-tts`
- **Requirements:** GPU (CUDA) recommended, ~4GB VRAM, Python 3.11+
- **Integration:** Python API - `ChatterboxTTS.from_pretrained(...)`
- **Use Case:** Primary TTS engine for high-quality voice generation on the fly

#### **Coqui TTS** (XTTS) - **PRIMARY RECOMMENDATION**
- **Quality:** Flexible framework with powerful XTTS model for multilingual cloning
- **Features:** Many pre-trained voices, allows fine-tuning on custom data
- **Install:** `pip install coqui-tts`
- **Requirements:** GPU recommended for real-time
- **Integration:** Python API or CLI server
- **Use Case:** General TTS engine, supports future fine-tuning

#### **Tortoise TTS** - **OPTIONAL (HQ Mode)**
- **Quality:** Ultra-realistic but slower synthesis
- **Features:** Multi-voice TTS system, emphasis on quality
- **Install:** `pip install tortoise-tts`
- **Requirements:** GPU recommended, slower than alternatives
- **Integration:** Python API
- **Use Case:** "HQ Render" mode when maximum quality is needed over speed

#### **OpenVoice AI** - **LOWER PRIORITY**
- **Quality:** Lower than Chatterbox/Coqui
- **Use Case:** Quick cloning option (less emphasized for pro quality)

#### **Real-Time Voice Cloning (RTVC)** - **LOWER PRIORITY**
- **Quality:** Moderate (intelligible but less natural)
- **Use Case:** Lightweight applications, learning/starting point

### Speech-to-Text (Transcription) Engines

#### **Whisper** (with faster-whisper) - **DEFAULT STT ENGINE**
- **Quality:** Highly accurate, general-purpose
- **Features:** Speech-to-text, translation, language identification
- **Install:** `pip install openai-whisper` or `pip install faster-whisper`
- **Requirements:** GPU recommended but works on CPU
- **Integration:** Python API
- **Use Case:** Default transcription engine

#### **whisper.cpp** (GGML) - **CPU-ONLY / REAL-TIME**
- **Quality:** Same as Whisper but optimized for CPU
- **Features:** Quantized models (4-bit/8-bit), real-time transcription feasible
- **Install:** Build from source or `pip install whisper-cpp-python`
- **Requirements:** CPU-only (no GPU needed)
- **Integration:** C/C++ library or Python wrapper
- **Use Case:** Real-time transcription on CPU, desktop app without GPU requirement

#### **WhisperX** - **ADVANCED FEATURES**
- **Quality:** Same as Whisper + word-level timestamps
- **Features:** Word-level timestamps, speaker diarization, forced alignment
- **Install:** `pip install whisperx`
- **Requirements:** GPU recommended for diarization
- **Integration:** Python API - `whisperx.transcribe(audio, model="medium")`
- **Use Case:** Precise word timings, speaker separation for advanced editing

#### **Vosk** - **LOW-END MACHINES**
- **Quality:** Less accurate than Whisper but fast and lightweight
- **Features:** 20+ languages, real-time decoding on CPU, streaming API
- **Install:** `pip install vosk`
- **Requirements:** CPU-friendly, minimal hardware (Raspberry Pi capable)
- **Integration:** Python API, bindings for multiple languages
- **Use Case:** Basic offline dictation on very low-end machines

### Inference Optimization Frameworks

#### **PyTorch** - **PRIMARY FRAMEWORK**
- **Use:** Most model interactions (all recommended models have PyTorch versions)
- **Install:** `pip install torch` (+ CUDA version if needed)
- **Integration:** Python API, C++ LibTorch available

#### **ONNX Runtime** - **OPTIMIZATION BACKEND**
- **Use:** Convert models to ONNX for faster CPU/GPU inference
- **Install:** `pip install onnxruntime` (CPU) or `onnxruntime-gpu` (CUDA)
- **Integration:** Load ONNX models for optimized deployment
- **Use Case:** Production deployment with minimal overhead

#### **CTranslate2** - **WHISPER ACCELERATION**
- **Use:** 4-8× speedup for Whisper with minimal accuracy loss
- **Install:** `pip install ctranslate2`
- **Integration:** Use faster-whisper (CTranslate2 backend)
- **Use Case:** Reduce transcription latency

#### **TensorRT** - **OPTIONAL (NVIDIA GPUs)**
- **Use:** Maximum performance on NVIDIA GPUs
- **Install:** NVIDIA TensorRT toolkit
- **Integration:** Convert models to TensorRT engine
- **Use Case:** Optional improvement for later stage (complex build process)

## Integration Strategy for VoiceStudio Backend

### Recommended Architecture

```
VoiceStudio Backend (Python FastAPI)
├── TTS Engines (Primary)
│   ├── Chatterbox TTS (default, high quality)
│   ├── Coqui TTS/XTTS (alternative, fine-tuning support)
│   └── Tortoise TTS (HQ render mode, optional)
│
├── Transcription Engines (Primary)
│   ├── Whisper (faster-whisper with CTranslate2) - default
│   ├── whisper.cpp - CPU-only fallback
│   ├── WhisperX - advanced features (word timestamps, diarization)
│   └── Vosk - low-end machine fallback
│
└── Optimization Backends
    ├── PyTorch (primary framework)
    ├── ONNX Runtime (optimized deployment)
    └── CTranslate2 (Whisper acceleration)
```

### Backend API Endpoints

```python
# TTS/Synthesis
POST /api/voice/synthesize
  - engine: "chatterbox" | "coqui" | "tortoise"
  - profile_id: string
  - text: string
  - language: string (optional)
  - emotion: float (optional, for Chatterbox)

# Transcription
POST /api/transcribe
  - engine: "whisper" | "whisperx" | "whisper-cpp" | "vosk"
  - audio_file: file
  - language: string (optional)
  - word_timestamps: bool (optional, for WhisperX)
  - diarization: bool (optional, for WhisperX)

# Voice Cloning (Training)
POST /api/voice/train
  - engine: "coqui" | "rvc"
  - audio_samples: files[]
  - profile_id: string
```

### GPU Acceleration Toggles

The UI should provide GPU acceleration toggles that map to:
- **CUDA** in PyTorch libraries (with fallback to CPU/quantized modes)
- **ONNX Runtime GPU** provider when using ONNX models
- **TensorRT** engine when available (optional, advanced)

### Workflow Examples

1. **Voice Synthesis:**
   - User selects voice profile → Text input → Backend calls Chatterbox/Coqui TTS → Audio generated → Added to timeline

2. **Transcription:**
   - User opens audio file → Backend calls Whisper (faster-whisper) → Transcript returned → Displayed in editor with optional word timestamps

3. **Advanced Editing:**
   - User requests word-level alignment → Backend calls WhisperX → Returns words with timestamps → UI aligns transcript to waveform

## Implementation Notes

- All recommended tools are **free, self-hosted, offline solutions** - no API keys needed
- Aligns with VoiceStudio's **local-first, privacy-focused approach**
- Modular design allows swapping engines as models evolve
- GPU acceleration is optional but recommended for real-time use
- CPU fallbacks ensure functionality on lower-end hardware

## Plugin System Integration

Each engine can be implemented as a backend plugin:
- `backend/plugins/chatterbox_tts/`
- `backend/plugins/coqui_tts/`
- `backend/plugins/whisper_transcribe/`
- `backend/plugins/whisperx_transcribe/`

This allows:
- Dynamic engine selection
- Easy addition of new engines
- User-configurable engine preferences
- Per-profile engine assignment

