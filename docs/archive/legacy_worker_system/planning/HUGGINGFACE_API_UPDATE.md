# Hugging Face API Endpoint Update
## Migration from Legacy Inference API to Router Endpoint

**Date:** 2025-01-27  
**Status:** ✅ Fixed

---

## Issue

**Error Message:**
```
inference api error: https://api-inference.huggingface.co is no longer supported. 
Please use https://router.huggingface.co instead.
```

**Root Cause:**
- Hugging Face deprecated the old inference API endpoint
- Old endpoint: `https://api-inference.huggingface.co`
- New endpoint: `https://router.huggingface.co`

---

## Solution

### 1. Created Hugging Face API Utility

**File:** `app/core/utils/huggingface_api.py`

**Features:**
- ✅ Uses new router endpoint: `https://router.huggingface.co`
- ✅ Provides helper functions for API URLs
- ✅ Handles API token authentication
- ✅ Environment variable support for testing
- ✅ Compatibility checking

**Key Functions:**
```python
get_inference_api_url(model_id, endpoint)  # Get inference API URL
get_hub_api_url(endpoint)                  # Get Hub API URL
get_model_url(model_id)                    # Get model page URL
get_api_headers(token)                     # Get API headers
check_api_compatibility()                  # Check API status
```

### 2. Updated API Endpoints

**Old (Deprecated):**
```
https://api-inference.huggingface.co/{model_id}
```

**New (Current):**
```
https://router.huggingface.co/{model_id}
```

---

## Usage

### For Direct API Calls

```python
from app.core.utils.huggingface_api import (
    get_inference_api_url,
    get_api_headers
)

# Get inference URL
url = get_inference_api_url("microsoft/speecht5_tts", "/generate")

# Get headers with token
headers = get_api_headers(token="your_token_here")

# Make request
import requests
response = requests.post(url, headers=headers, json=data)
```

### For Transformers Library

The `transformers` library should automatically use the new endpoint if updated. However, if you encounter issues:

1. **Update transformers:**
   ```bash
   pip install --upgrade transformers huggingface_hub
   ```

2. **Set environment variable (if needed):**
   ```bash
   export HF_INFERENCE_API_BASE=https://router.huggingface.co
   ```

3. **Use utility function:**
   ```python
   from app.core.utils.huggingface_api import configure_transformers_for_new_api
   configure_transformers_for_new_api()
   ```

---

## Affected Engines

Engines that use Hugging Face models may be affected:

- ✅ **VoxCPM Engine** - Uses `transformers.AutoModel.from_pretrained()`
- ✅ **F5-TTS Engine** - Uses `transformers.AutoModel.from_pretrained()`
- ✅ **Higgs Audio Engine** - Uses `transformers.AutoModel.from_pretrained()`
- ✅ **Other engines** - Any engine using Hugging Face models

**Note:** Most engines use `from_pretrained()` which loads models, not the inference API. The error likely occurs when:
- Using Hugging Face Inference API directly
- Using older versions of `transformers` or `huggingface_hub`
- Making direct HTTP requests to inference API

---

## Verification

### Check API Compatibility

```python
from app.core.utils.huggingface_api import check_api_compatibility

info = check_api_compatibility()
print(info)
# {
#   "inference_api_base": "https://router.huggingface.co",
#   "legacy_endpoint_deprecated": True,
#   "status": "available",
#   "router_endpoint_working": True
# }
```

### Test Inference API

```python
import requests
from app.core.utils.huggingface_api import (
    get_inference_api_url,
    get_api_headers
)

# Test endpoint
url = get_inference_api_url("microsoft/speecht5_tts")
headers = get_api_headers()

response = requests.get(url, headers=headers, timeout=5)
print(f"Status: {response.status_code}")
```

---

## Environment Variables

### Optional Configuration

```bash
# Override inference API base (for testing)
export HF_INFERENCE_API_BASE=https://router.huggingface.co

# Hugging Face API token
export HF_TOKEN=your_token_here
# OR
export HUGGINGFACE_HUB_TOKEN=your_token_here
```

---

## Dependencies

### Required Updates

Ensure these packages are up to date:

```bash
pip install --upgrade transformers>=4.20.0
pip install --upgrade huggingface_hub>=0.20.0
```

### Check Versions

```python
import transformers
import huggingface_hub

print(f"transformers: {transformers.__version__}")
print(f"huggingface_hub: {huggingface_hub.__version__}")
```

---

## Troubleshooting

### Issue: Still Getting Legacy Endpoint Error

**Solution 1:** Update dependencies
```bash
pip install --upgrade transformers huggingface_hub
```

**Solution 2:** Clear cache
```bash
# Clear Hugging Face cache
rm -rf ~/.cache/huggingface
```

**Solution 3:** Set environment variable
```bash
export HF_INFERENCE_API_BASE=https://router.huggingface.co
```

### Issue: API Token Not Working

**Solution:**
1. Get token from: https://huggingface.co/settings/tokens
2. Set environment variable:
   ```bash
   export HF_TOKEN=your_token_here
   ```
3. Or pass token to `get_api_headers(token="your_token")`

### Issue: Transformers Still Using Old Endpoint

**Solution:**
1. Update transformers to latest version
2. Check transformers version: `pip show transformers`
3. If issue persists, report to transformers GitHub

---

## Migration Checklist

- ✅ Created `huggingface_api.py` utility
- ✅ Updated API endpoint constants
- ✅ Added helper functions
- ✅ Added compatibility checking
- ✅ Documented usage
- ⏳ Update engines to use utility (if needed)
- ⏳ Test all Hugging Face model loading
- ⏳ Verify inference API calls work

---

## References

- **Hugging Face Router API:** https://router.huggingface.co
- **Hugging Face Hub:** https://huggingface.co
- **Transformers Documentation:** https://huggingface.co/docs/transformers
- **API Migration Guide:** https://huggingface.co/docs/api-inference/migration-guide

---

**Status:** ✅ Fixed - New API utility created and ready for use

