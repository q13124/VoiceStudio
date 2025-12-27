# Phase 7: Engine Implementation Tasks
## Quick Reference for All Workers

**Date:** 2025-11-23  
**Status:** 🟢 Ready to Begin  
**Total Engines:** 44 engines

---

## 🚨 CRITICAL: This is Your Current Priority

**All workers should see Phase 7 engine tasks at the TOP of their prompt files.**

If you don't see engine tasks, check:
1. `docs/governance/WORKER_1_PROMPT_PERFORMANCE_MEMORY_ERROR.md` - Lines 1-50
2. `docs/governance/WORKER_2_PROMPT_UI_UX_POLISH.md` - Lines 1-50
3. `docs/governance/WORKER_3_PROMPT_DOCUMENTATION_PACKAGING.md` - Lines 1-50

---

## 👷 Worker 1: Audio Engines (15 engines)

**Location in Prompt:** Top of file (after header)

**Engines to Implement:**
1. Higgs Audio
2. F5-TTS
3. VoxCPM
4. Parakeet
5. Silero Models
6. GPT-SoVITS
7. MockingBird Clone
8. whisper.cpp
9. Whisper UI
10. Aeneas
11. MaryTTS
12. Festival/Flite
13. eSpeak NG
14. RHVoice
15. OpenVoice (update if needed)

**See:** `docs/governance/WORKER_1_PROMPT_PERFORMANCE_MEMORY_ERROR.md` (lines 1-50)

---

## 👷 Worker 2: Legacy Audio + Image Engines (18 engines)

**Location in Prompt:** Top of file (after header)

**Legacy Audio (5):**
1. MaryTTS
2. Festival/Flite
3. eSpeak NG
4. RHVoice
5. OpenVoice

**Image Engines (13):**
1. SDXL ComfyUI
2. ComfyUI
3. AUTOMATIC1111 WebUI
4. SD.Next
5. InvokeAI
6. Fooocus
7. LocalAI
8. SDXL
9. Realistic Vision
10. OpenJourney
11. Stable Diffusion CPU-only
12. FastSD CPU
13. Real-ESRGAN

**See:** `docs/governance/WORKER_2_PROMPT_UI_UX_POLISH.md` (lines 1-50)

---

## 👷 Worker 3: Video Engines + Cloud VC (10 engines)

**Location in Prompt:** Top of file (after header)

**Video Engines (8):**
1. Stable Video Diffusion (SVD)
2. Deforum
3. First Order Motion Model (FOMM)
4. SadTalker
5. DeepFaceLab
6. MoviePy
7. FFmpeg with AI Plugins
8. Video Creator (prakashdk)

**Voice Conversion Cloud (2):**
9. Voice.ai
10. Lyrebird (Descript)

**See:** `docs/governance/WORKER_3_PROMPT_DOCUMENTATION_PACKAGING.md` (lines 1-50)

---

## 📋 Implementation Requirements

**For EVERY Engine:**
1. Create `app/core/engines/{engine_id}_engine.py`
2. Inherit from `EngineProtocol`
3. Implement ALL methods (NO stubs/placeholders/TODOs)
4. Create backend API endpoints (if needed)
5. Test engine individually
6. Update documentation

**100% Completion Rule:**
- ❌ NO TODO comments
- ❌ NO NotImplementedException
- ❌ NO PLACEHOLDER text
- ❌ NO empty methods
- ✅ ALL methods fully implemented
- ✅ ALL engines tested

---

## 📁 Key Documents

1. **`docs/governance/ENGINE_IMPLEMENTATION_PLAN.md`** - Complete plan
2. **`docs/governance/ENGINE_IMPLEMENTATION_SUMMARY.md`** - Summary
3. **`requirements_engines.txt`** - All dependencies
4. **`docs/governance/COMPLETE_ENGINE_LIST.md`** - All 44 engines listed

---

## ✅ Verification

**To verify engines are in your prompt:**
1. Open your worker prompt file
2. Check lines 1-50
3. You should see "PHASE 7: ENGINE IMPLEMENTATION" section
4. You should see your engine list

**If you don't see it:**
- Check the file was updated
- Look for "PHASE 7" or "ENGINE IMPLEMENTATION" in the file
- Contact overseer if still not visible

---

**Status:** ✅ Engines added to all worker prompts  
**Location:** Top of each worker prompt file (lines 1-50)

