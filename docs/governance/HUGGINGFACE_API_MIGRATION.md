# Hugging Face API Migration Guide
## Updating from api-inference.huggingface.co to router.huggingface.co

**Date:** 2025-01-27  
**Status:** Migration Required  
**Issue:** `https://api-inference.huggingface.co` is no longer supported

---

## 🔍 Problem

**Error Message:**
```
inference api error: https://api-inference.huggingface.co is no longer supported. 
Please use https://router.huggingface.co instead.
```

**Root Cause:**
Hugging Face has deprecated the old inference API endpoint and migrated to a new router-based system.

---

## ✅ Solution

### Step 1: Update huggingface_hub Library

The `huggingface_hub` library has been updated to use the new endpoint. Update to the latest version:

```bash
pip install --upgrade huggingface_hub
```

**Minimum Version:** `huggingface_hub >= 0.20.0` (includes new InferenceClient)

### Step 2: Update Code Using Inference API

If you have any code directly using the old Inference API, update it:

#### Old Code (Deprecated):
```python
from huggingface_hub import InferenceApi

api = InferenceApi(repo_id="model-name")
result = api(inputs="text")
```

#### New Code (Recommended):
```python
from huggingface_hub import InferenceClient

client = InferenceClient(model="model-name")
result = client.text_generation("text")
```

### Step 3: Update transformers Library

Ensure you're using a recent version of transformers that works with the new endpoint:

```bash
pip install --upgrade transformers
```

**Recommended Version:** `transformers >= 4.30.0`

---

## 🔧 VoiceStudio-Specific Updates

### Current Status

**Good News:** VoiceStudio engines use `transformers.AutoModel.from_pretrained()` which should automatically use the new endpoint if libraries are up-to-date.

**Engines Using Transformers:**
- `higgs_audio_engine.py`
- `f5_tts_engine.py`
- `voxcpm_engine.py`
- `xtts_engine.py`
- `tortoise_engine.py`
- `svd_engine.py`
- `deforum_engine.py`

### Required Actions

1. **Update requirements_engines.txt:**
   ```txt
   huggingface_hub>=0.20.0
   transformers>=4.30.0
   ```

2. **Verify No Direct API Calls:**
   - Check for any direct HTTP requests to `api-inference.huggingface.co`
   - Update any found to use `router.huggingface.co/hf-inference`

3. **Test Model Loading:**
   - Test each engine that uses transformers
   - Verify models load correctly from Hugging Face Hub

---

## 📋 Migration Checklist

- [ ] Update `huggingface_hub` to latest version
- [ ] Update `transformers` to latest version
- [ ] Check for direct API endpoint usage
- [ ] Update any InferenceApi usage to InferenceClient
- [ ] Test model loading for all engines
- [ ] Update requirements_engines.txt
- [ ] Test inference operations

---

## 🔗 References

- **Hugging Face Migration Guide:** https://huggingface.co/docs/huggingface_hub/main/concepts/migration
- **New InferenceClient Docs:** https://huggingface.co/docs/huggingface_hub/main/en/package_reference/inference_client

---

## 🚀 Quick Fix

Run this command to update all Hugging Face libraries:

```bash
pip install --upgrade huggingface_hub transformers
```

Then restart your application.

---

**Status:** Ready for migration  
**Priority:** High - Required for Hugging Face model access

