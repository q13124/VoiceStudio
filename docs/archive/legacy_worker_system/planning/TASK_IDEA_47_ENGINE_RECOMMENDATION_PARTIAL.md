# IDEA 47: Quality-Based Engine Recommendation System - PARTIAL ✅

**Date:** 2025-01-27  
**Status:** ✅ **BACKEND COMPLETE** | ⏳ **UI PENDING**  
**Priority:** 🔴 High  
**Worker:** Overseer

---

## 🎯 Implementation Summary

Successfully implemented backend for quality-based engine recommendation system. Backend endpoint and models are complete. UI integration is pending.

---

## ✅ Completed Features

### 1. Backend Endpoint Created
- ✅ `backend/api/routes/engines.py` - New engine management routes
- ✅ `POST /api/engines/recommend` - Engine recommendation endpoint
- ✅ `GET /api/engines/list` - List all available engines
- ✅ `GET /api/engines/compare` - Compare multiple engines side-by-side

### 2. Recommendation Algorithm
- ✅ Quality-based engine scoring
- ✅ Minimum requirements checking (MOS, Similarity, Naturalness)
- ✅ Quality tier matching ("fast", "standard", "high", "ultra")
- ✅ Speed preference support
- ✅ Recommendation reasoning generation

### 3. Models Created
- ✅ `backend/api/models_additional.py` - Pydantic models:
  - `EngineRecommendationRequest`
  - `EngineQualityEstimate`
  - `EngineRecommendation`
  - `EngineRecommendationResponse`
- ✅ `src/VoiceStudio.Core/Models/QualityModels.cs` - C# models updated:
  - `EngineRecommendationRequest` (updated with TaskType)
  - `EngineQualityEstimate` (new)
  - `EngineRecommendation` (new)
  - `EngineRecommendationResponse` (updated with list of recommendations)

### 4. Backend Client Integration
- ✅ `src/VoiceStudio.App/Services/BackendClient.cs` - Updated to use POST endpoint
- ✅ `src/VoiceStudio.Core/Services/IBackendClient.cs` - Interface already had method

---

## 📁 Files Created/Modified

### Backend
1. **`backend/api/routes/engines.py`** (NEW)
   - Engine recommendation endpoint
   - Engine listing endpoint
   - Engine comparison endpoint

2. **`backend/api/models_additional.py`** (MODIFIED)
   - Added engine recommendation models

3. **`backend/api/main.py`** (MODIFIED)
   - Added `engines` router import
   - Registered `engines.router`

### Frontend
1. **`src/VoiceStudio.Core/Models/QualityModels.cs`** (MODIFIED)
   - Updated `EngineRecommendationRequest` with `TaskType`
   - Added `EngineQualityEstimate` class
   - Added `EngineRecommendation` class
   - Updated `EngineRecommendationResponse` with list of recommendations

2. **`src/VoiceStudio.App/Services/BackendClient.cs`** (MODIFIED)
   - Updated `GetEngineRecommendationAsync` to use POST endpoint

---

## 🔄 Recommendation Algorithm

The recommendation algorithm:

1. **Filters engines by task type** (e.g., "tts", "voice_cloning")
2. **Extracts quality estimates** from engine manifests:
   - MOS score estimate
   - Similarity estimate
   - Naturalness estimate
   - Speed estimate
3. **Checks minimum requirements**:
   - Validates MOS score meets minimum
   - Validates similarity meets minimum
   - Validates naturalness meets minimum
4. **Calculates recommendation score**:
   - Quality tier matching (30%)
   - MOS score contribution (30%)
   - Similarity contribution (20%)
   - Naturalness contribution (20%)
   - Speed preference adjustment (±20%)
5. **Sorts by score** (descending)
6. **Generates reasoning** for each recommendation

---

## 📊 API Endpoints

### POST `/api/engines/recommend`
**Request:**
```json
{
  "task_type": "tts",
  "min_mos_score": 4.0,
  "min_similarity": 0.8,
  "min_naturalness": 0.75,
  "prefer_speed": false,
  "quality_tier": "high"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "engine_id": "tortoise",
      "engine_name": "Tortoise TTS",
      "recommendation_score": 0.95,
      "quality_estimate": {
        "mos_score": 4.8,
        "similarity": 0.92,
        "naturalness": 0.88,
        "speed_estimate": "slow"
      },
      "meets_requirements": true,
      "reasoning": "Recommended: Matches quality tier 'high', MOS: 4.80, Similarity: 0.92, Naturalness: 0.88, High quality (slower)"
    }
  ],
  "total_engines": 3,
  "matching_engines": 2
}
```

### GET `/api/engines/list`
Returns list of all available engines.

### GET `/api/engines/compare?engines=xtts,chatterbox,tortoise&task_type=tts`
Compares multiple engines side-by-side.

---

## ⏳ Pending UI Implementation

The following UI components need to be created:

1. **EngineRecommendationView.xaml** - UI component for displaying recommendations
2. **EngineRecommendationViewModel.cs** - ViewModel for recommendation logic
3. **Quality Goal Input** - UI for setting MOS, Similarity, Naturalness targets
4. **Recommendation Display** - List/cards showing recommended engines with scores
5. **Integration with VoiceSynthesisView** - Add recommendation button/panel

---

## 🧪 Testing Notes

- ✅ No linting errors
- ✅ Backend endpoint compiles successfully
- ✅ Models match between backend and frontend
- ⏳ **Manual testing required:**
  - Test recommendation endpoint with various quality requirements
  - Verify recommendation scores are calculated correctly
  - Test engine filtering by task type
  - Verify minimum requirements checking

---

## 🚀 Next Steps

1. **Create UI Component:**
   - Create `EngineRecommendationView.xaml` with quality goal inputs
   - Create `EngineRecommendationViewModel.cs` with recommendation logic
   - Display recommendations in a list/card format

2. **Integrate with VoiceSynthesisView:**
   - Add "Get Recommendations" button
   - Show recommendations when quality goals are set
   - Allow selecting recommended engine directly

3. **Enhancement (Optional):**
   - Add engine quality comparison chart
   - Show historical quality data per engine
   - Add "Apply Recommendation" button

---

## 📚 Related Documents

- `docs/governance/BRAINSTORMER_IDEAS.md` - IDEA 47 specification
- `docs/governance/HIGH_PRIORITY_IMPLEMENTATION_PLAN.md` - Implementation plan
- `app/core/engines/router.py` - Engine router with `select_engine_by_quality()` method
- `engines/README.md` - Engine manifest documentation

---

## ✅ Success Criteria Met (Backend)

- ✅ Backend endpoint for engine recommendations
- ✅ Quality-based recommendation algorithm
- ✅ Minimum requirements checking
- ✅ Quality tier matching
- ✅ Speed preference support
- ✅ Recommendation reasoning generation
- ✅ Engine listing and comparison endpoints
- ✅ Models match between backend and frontend
- ✅ No placeholders or stubs - fully implemented

---

**Last Updated:** 2025-01-27  
**Status:** ✅ **BACKEND COMPLETE** | ⏳ **UI PENDING**

