# Audio Engines Added - Complete List
## All Audio/TTS/STT/VC Engines - 2025-11-23

**Status:** ✅ **All Manifests Created** - Ready for Implementation  
**Total Audio Engines:** 16 engines  
**Priority:** High - Add to implementation roadmap

---

## 📋 Audio Engines Added

### TTS (Text-to-Speech) Engines (11 engines)

#### Already Integrated:
1. ✅ **XTTS v2 (Coqui TTS)** - Already has manifest and implementation
2. ✅ **Chatterbox TTS** - Already has manifest and implementation
3. ✅ **Tortoise TTS** - Already has manifest and implementation
4. ✅ **Piper (Rhasspy)** - Already has manifest (updated description)
5. ✅ **OpenVoice** - Already has manifest
6. ✅ **Whisper** - Already has manifest (STT)

#### Newly Added:
7. ✅ **Higgs Audio** - High-fidelity, zero-shot TTS (manifest created)
8. ✅ **F5-TTS** - Modern expressive neural TTS (manifest created)
9. ✅ **VoxCPM** - Chinese and multilingual TTS (manifest created)
10. ✅ **Parakeet** - Fast and efficient TTS (manifest created)
11. ✅ **MaryTTS** - Classic open-source multilingual TTS (manifest created)
12. ✅ **Festival/Flite** - Legacy TTS system (manifest created)
13. ✅ **eSpeak NG** - Compact multilingual TTS (manifest created)
14. ✅ **RHVoice** - Multilingual TTS with high-quality voices (manifest created)
15. ✅ **Silero Models** - Fast, high-quality multilingual TTS (manifest created)

### VC (Voice Conversion) Engines (4 engines)

16. ✅ **GPT-SoVITS** - Voice conversion and fine-tuning (manifest created)
17. ✅ **MockingBird Clone** - Real-time voice cloning (manifest created)
18. ✅ **Voice.ai** - Real-time voice conversion (manifest created)
19. ✅ **Lyrebird (Descript)** - High-quality voice cloning (manifest created)

### STT (Speech-to-Text) Engines (2 engines)

20. ✅ **Whisper** - Already has manifest (Python implementation)
21. ✅ **whisper.cpp** - Already has manifest (C++ implementation)
22. ✅ **Whisper UI** - User interface wrapper for Whisper (manifest created)

### Alignment/Subtitle Engines (1 engine)

23. ✅ **Aeneas** - Already has manifest (audio-text alignment)

---

## 📁 Files Created

### Engine Manifests (15 new files):
1. `engines/audio/higgs_audio/engine.manifest.json`
2. `engines/audio/f5_tts/engine.manifest.json`
3. `engines/audio/voxcpm/engine.manifest.json`
4. `engines/audio/gpt_sovits/engine.manifest.json`
5. `engines/audio/mockingbird/engine.manifest.json`
6. `engines/audio/parakeet/engine.manifest.json`
7. `engines/audio/marytts/engine.manifest.json`
8. `engines/audio/festival/engine.manifest.json`
9. `engines/audio/espeak_ng/engine.manifest.json`
10. `engines/audio/rhvoice/engine.manifest.json`
11. `engines/audio/silero/engine.manifest.json`
12. `engines/audio/voice_ai/engine.manifest.json`
13. `engines/audio/lyrebird/engine.manifest.json`
14. `engines/audio/whisper_ui/engine.manifest.json`
15. Updated: `engines/audio/piper/engine.manifest.json` (description updated)

### Documentation Updated:
- ✅ `engines/README.md` - Audio engines section updated
- ✅ `docs/governance/ENGINE_INTEGRATION_SUMMARY.md` - Updated totals

---

## 🎯 Engine Categories

### High-Quality TTS (GPU Recommended):
- XTTS v2, Chatterbox TTS, Tortoise TTS
- Higgs Audio, F5-TTS, VoxCPM
- GPT-SoVITS, MockingBird, Voice.ai, Lyrebird

### Fast/Lightweight TTS (CPU Friendly):
- Piper, OpenVoice
- Parakeet, Silero Models
- MaryTTS, Festival/Flite, eSpeak NG, RHVoice

### Voice Conversion:
- GPT-SoVITS, MockingBird, Voice.ai, Lyrebird

### Speech-to-Text:
- Whisper (Python), whisper.cpp (C++), Whisper UI

---

## 📊 Implementation Priority

### High Priority (Core Features):
1. **Silero Models** - Fast, many languages, CPU-friendly
2. **Higgs Audio** - High-fidelity zero-shot
3. **F5-TTS** - Modern expressive TTS
4. **GPT-SoVITS** - Voice conversion

### Medium Priority (Specialized):
5. **VoxCPM** - Chinese/multilingual
6. **Parakeet** - Fast synthesis
7. **MockingBird** - Real-time cloning

### Low Priority (Legacy/Accessibility):
8. **MaryTTS** - Classic TTS
9. **Festival/Flite** - Legacy system
10. **eSpeak NG** - Accessibility
11. **RHVoice** - Multilingual

### Note (May Require API Keys):
- **Voice.ai** - May require API key (prefer local)
- **Lyrebird** - May require API key (prefer local)

---

## 🔧 Technical Requirements

### Dependencies:
```bash
# High-quality TTS
pip install torch torchaudio transformers

# Voice conversion
pip install torch librosa

# PaddlePaddle (Parakeet)
pip install paddlepaddle paddlespeech

# Legacy TTS (system packages)
# Festival/Flite, eSpeak NG, RHVoice - require system installation
```

### Model Storage:
All models stored in:
- `%PROGRAMDATA%\VoiceStudio\models\{engine_id}\`

### Device Requirements:
- **GPU Required:** XTTS, Chatterbox, Tortoise, Higgs, F5-TTS, GPT-SoVITS, MockingBird
- **GPU Recommended:** VoxCPM, Voice.ai, Lyrebird
- **GPU Optional:** Piper, OpenVoice, Parakeet, Silero, Whisper
- **CPU Only:** MaryTTS, Festival/Flite, eSpeak NG, RHVoice

---

## 📝 Notes

- All engines are 100% local (no web APIs)
- Voice.ai and Lyrebird may have cloud options but local inference preferred
- Legacy engines (Festival, eSpeak, RHVoice) are lightweight and CPU-friendly
- Silero Models are fast and support many languages
- Engines will be automatically discovered via manifests

---

**Status:** ✅ All Manifests Complete - Ready for Implementation  
**Next:** Assign to workers for engine implementation

