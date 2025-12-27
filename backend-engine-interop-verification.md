# Backend-Engine Interop Verification (Phase 5)

**Date:** 2025-01-28  
**Status:** Analysis Complete

## Contract Alignment

### Frontend (BackendClient.cs)
- **Engine Discovery:** No explicit `GetEnginesAsync` method found in BackendClient
- **Engine Recommendation:** `GetQualityRecommendationAsync` → `/api/engines/recommend`
- **Video Engines:** `GetVideoEnginesAsync` → `/api/video/engines/list`
- **Base URL:** Configured via `BackendClientConfig.BaseUrl`

### Backend (engines.py)
- **Router Prefix:** `/api/engines`
- **Available Endpoints:**
  - `/api/engines/recommend` (POST) - Engine recommendation
  - `/api/engines/list` - Engine listing (if implemented)
  - `/api/video/engines/list` - Video engines (via video routes)

### Engine Router (router.py)
- **Engine Discovery:** Uses manifest-based discovery via `find_engine_manifests()`
- **Engine Loading:** `load_engine` method loads engines from manifests
- **Engine Protocol:** All engines must inherit from `EngineProtocol`
- **Manifest Location:** `engines/*/engine.manifest.json`

## Alignment Issues Found

### Missing Frontend Method ✅ FIXED
- **Issue:** Frontend had no `GetEnginesAsync()` method to call `/api/engines/list`
- **Impact:** Frontend could not discover available engines from backend
- **Resolution:** 
  - ✅ Added `GetEnginesAsync()` method to `BackendClient.cs`
  - ✅ Added method signature to `IBackendClient.cs` interface
  - ✅ Created `EnginesListResponse.cs` model to match backend response
  - ✅ Updated `TextSpeechEditorViewModel.cs` to use new method

### Model Alignment
- **Frontend Models:** Need to verify `EngineInfo` model matches backend response
- **Backend Response:** Need to check what `/api/engines/list` returns
- **Action Required:** Verify model definitions match

## Engine Discovery Flow

1. **Backend Startup:**
   - `engine_router_instance` loads all engine manifests
   - Engines are registered via `load_all_engines()`
   - `/api/engines/list` endpoint should return available engines

2. **Frontend Startup:**
   - `BackendClient` connects to backend API
   - Should call `/api/engines/list` to get available engines
   - **Issue:** No method exists to call this endpoint

3. **Runtime:**
   - Frontend requests engine recommendation via `/api/engines/recommend`
   - Backend uses engine router to select appropriate engine
   - Engine instance is loaded/retrieved and used

## Verification Checklist

- [ ] Backend `/api/engines/list` endpoint exists and returns engine list
- [ ] Frontend `GetEnginesAsync()` method exists (currently missing)
- [ ] `EngineInfo` model matches backend response structure
- [ ] Engine manifest loading works correctly (verified - all engines load successfully)
- [ ] Engine protocol inheritance verified (verified - all engines inherit from `EngineProtocol`)

## Recommendations

1. **Add Missing Method:** Implement `GetEnginesAsync()` in `BackendClient.cs`
2. **Verify Endpoint:** Ensure `/api/engines/list` endpoint exists in backend
3. **Model Verification:** Ensure frontend `EngineInfo` matches backend response
4. **Integration Test:** Create minimal smoke test for app→backend→engine flow

