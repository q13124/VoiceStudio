# CUDA Compatibility Audit — Phase 9 Sprint 4

**Date**: 2026-02-21  
**Target**: RTX 5070 Ti (Blackwell, sm_120), Driver 591.74, CUDA 13.1

---

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| torch.cuda | Check at runtime | Use `torch.cuda.is_available()` |
| GPU detection | resource_manager.py | Uses torch.cuda.get_device_properties(0) |
| Workload balancer | workload_balancer.py | Routes to GPU/CPU based on availability |
| sm_120 support | Verify torch build | PyTorch wheels may need CUDA 12.x build |

---

## GPU Detection

- **Location**: `app/core/runtime/resource_manager.py`
- **Logic**: `torch.cuda.is_available()` → `get_device_properties(0)` for VRAM
- **Fallback**: CPU when CUDA unavailable

---

## Recommendations

1. **RTX 5070 Ti (sm_120)**: Ensure PyTorch build supports compute capability 12.0. Check `torch.version.cuda` matches driver.
2. **CPU fallback**: Already supported; engines degrade gracefully when GPU unavailable.
3. **Model quantization**: XTTS, Whisper support FP16; INT8 optional for faster inference. Check engine adapters for `half()` or `quantize()` usage.

---

## Verification

```python
import torch
print(torch.cuda.is_available())
print(torch.version.cuda)
if torch.cuda.is_available():
    print(torch.cuda.get_device_properties(0))
```
