# Integration Testing Guide
## VoiceStudio Quantum+ Testing Documentation

**Last Updated:** 2025-01-27  
**Status:** Ready for Testing  
**Focus:** End-to-End UI-Backend Communication

---

## 🎯 Overview

This guide provides instructions for testing the integration between the WinUI 3 frontend and FastAPI backend, including voice cloning functionality and quality metrics.

---

## 📋 Prerequisites

### Backend Setup
1. **Python Environment**
   - Python 3.10+
   - Virtual environment activated
   - Dependencies installed: `pip install -r requirements.txt`

2. **Start Backend Server**
   ```bash
   cd backend/api
   uvicorn main:app --reload --port 8000
   ```
   - Server should start on `http://localhost:8000`
   - Verify: `curl http://localhost:8000/api/health`

### Frontend Setup
1. **Build C# Application**
   - Open solution in Visual Studio
   - Build solution (should compile without errors)
   - Ensure all NuGet packages restored

2. **Configuration**
   - Backend URL: `http://localhost:8000` (default in `BackendClientConfig`)
   - WebSocket URL: `ws://localhost:8000/ws` (default)

---

## 🧪 Test Scenarios

### 1. Health Check Test

**Objective:** Verify backend connectivity

**Steps:**
1. Launch VoiceStudio application
2. Navigate to Diagnostics panel (bottom panel)
3. Click "Check Health" button (if available) or wait for auto-check
4. Verify status shows "Backend API is healthy"

**Expected Results:**
- ✅ Health status displays correctly
- ✅ No error messages
- ✅ Status updates within 2 seconds

**Backend Verification:**
```bash
curl http://localhost:8000/api/health
# Should return: {"status": "ok", "version": "1.0"}
```

---

### 2. Profile Management Test

**Objective:** Test voice profile CRUD operations

**Steps:**
1. Navigate to Profiles panel (left panel)
2. **Create Profile:**
   - Click "Add Profile" or similar button
   - Enter profile name: "Test Profile"
   - Verify profile appears in list
3. **Read Profile:**
   - Select profile from list
   - Verify profile details display
4. **Update Profile:**
   - Modify profile name or language
   - Verify changes persist
5. **Delete Profile:**
   - Delete test profile
   - Verify removal from list

**Expected Results:**
- ✅ All CRUD operations work
- ✅ UI updates immediately
- ✅ Error messages display on failure
- ✅ Loading states show during operations

**Backend Verification:**
```bash
# List profiles
curl http://localhost:8000/api/profiles

# Create profile
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Profile", "language": "en"}'

# Get profile
curl http://localhost:8000/api/profiles/{profile_id}

# Update profile
curl -X PUT http://localhost:8000/api/profiles/{profile_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Delete profile
curl -X DELETE http://localhost:8000/api/profiles/{profile_id}
```

---

### 3. Project Management Test

**Objective:** Test project CRUD operations

**Steps:**
1. Navigate to Timeline panel (center panel)
2. **Create Project:**
   - Create new project: "Test Project"
   - Verify project appears
3. **Read Project:**
   - Select project
   - Verify project details
4. **Update Project:**
   - Modify project name or description
   - Verify changes persist
5. **Delete Project:**
   - Delete test project
   - Verify removal

**Expected Results:**
- ✅ All CRUD operations work
- ✅ Projects list updates correctly
- ✅ Error handling works

**Backend Verification:**
```bash
# List projects
curl http://localhost:8000/api/projects

# Create project
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "Test"}'

# Get project
curl http://localhost:8000/api/projects/{project_id}

# Update project
curl -X PUT http://localhost:8000/api/projects/{project_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Project"}'

# Delete project
curl -X DELETE http://localhost:8000/api/projects/{project_id}
```

---

### 4. Voice Synthesis Test

**Objective:** Test voice cloning synthesis with quality metrics

**Prerequisites:**
- At least one voice profile created
- Reference audio file available (optional)

**Steps:**
1. Select a voice profile
2. Enter text to synthesize: "Hello, this is a test."
3. Select engine: XTTS, Chatterbox, or Tortoise
4. Enable quality metrics (if option available)
5. Click "Synthesize" or similar button
6. Wait for synthesis to complete
7. Verify:
   - Audio file generated
   - Quality metrics displayed (if enabled)
   - No errors in Diagnostics panel

**Expected Results:**
- ✅ Synthesis completes successfully
- ✅ Audio file saved/returned
- ✅ Quality metrics available (MOS, similarity, naturalness)
- ✅ Duration matches audio length
- ✅ Error handling works for invalid inputs

**Backend Verification:**
```bash
# Synthesize voice
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "xtts",
    "profile_id": "profile_123",
    "text": "Hello, this is a test.",
    "language": "en"
  }'

# Should return:
# {
#   "audio_id": "...",
#   "audio_url": "/api/voice/audio/...",
#   "duration": 2.5,
#   "quality_metrics": {
#     "mos_score": 4.2,
#     "similarity": 0.87,
#     "naturalness": 0.82
#   }
# }
```

---

### 5. Quality Metrics Test

**Objective:** Test quality analysis endpoint

**Steps:**
1. Upload or select an audio file
2. Request quality analysis
3. Verify metrics returned:
   - MOS score (1.0-5.0)
   - Similarity (0.0-1.0) if reference provided
   - Naturalness (0.0-1.0)
   - SNR (dB)
   - Artifacts detection

**Expected Results:**
- ✅ All metrics calculated correctly
- ✅ Metrics within expected ranges
- ✅ Reference comparison works (if provided)

**Backend Verification:**
```bash
# Analyze audio
curl -X POST http://localhost:8000/api/voice/analyze \
  -F "audio_file=@test_audio.wav" \
  -F "metrics=mos,similarity,naturalness"

# Should return:
# {
#   "metrics": {
#     "mos": 4.2,
#     "similarity": 0.87,
#     "naturalness": 0.82,
#     "snr": 28.5
#   },
#   "quality_score": 0.85
# }
```

---

### 6. Error Handling Test

**Objective:** Verify graceful error handling

**Test Cases:**
1. **Backend Offline:**
   - Stop backend server
   - Attempt any operation
   - Verify error message displayed
   - Verify UI doesn't crash

2. **Invalid Profile ID:**
   - Attempt to synthesize with non-existent profile
   - Verify error message

3. **Invalid Engine:**
   - Attempt to use non-existent engine
   - Verify error message

4. **Network Timeout:**
   - Simulate slow network
   - Verify timeout handling
   - Verify retry logic (if implemented)

**Expected Results:**
- ✅ All errors handled gracefully
- ✅ User-friendly error messages
- ✅ No application crashes
- ✅ UI remains responsive

---

### 7. Performance Test

**Objective:** Verify acceptable performance

**Metrics to Check:**
- **Response Time:**
  - Health check: < 100ms
  - Profile list: < 500ms
  - Project list: < 500ms
  - Synthesis: < 30s (depends on engine)

- **UI Responsiveness:**
  - No UI freezing during operations
  - Loading indicators show
  - Progress feedback available

**Expected Results:**
- ✅ All operations complete within acceptable time
- ✅ UI remains responsive
- ✅ No memory leaks (check over time)

---

## 🔧 Test Tools

### Backend API Testing
- **curl** - Command-line HTTP client
- **Postman** - GUI API testing tool
- **httpie** - User-friendly HTTP client

### Frontend Testing
- **Visual Studio Test Explorer** - Unit tests
- **Manual Testing** - UI interaction
- **Performance Profiler** - Performance analysis

### Quality Metrics Testing
```bash
# Run quality metrics test suite
cd app/core/engines
python test_quality_metrics.py

# Should show:
# ✓ All tests passed!
```

---

## 📊 Test Checklist

### Phase 1: Core Backend & API Integration

- [ ] Health check endpoint works
- [ ] Profile CRUD operations work
- [ ] Project CRUD operations work
- [ ] Voice synthesis endpoint works
- [ ] Quality analysis endpoint works
- [ ] Error handling works
- [ ] Performance acceptable

### UI-Backend Communication

- [ ] ProfilesView loads profiles from backend
- [ ] ProfilesView creates/updates/deletes profiles
- [ ] DiagnosticsView shows backend health
- [ ] TimelineView loads projects from backend
- [ ] TimelineView creates/updates/deletes projects
- [ ] Error messages display correctly
- [ ] Loading states work

### Quality Metrics Integration

- [ ] Quality metrics calculated during synthesis
- [ ] Quality metrics displayed in UI (if implemented)
- [ ] Quality analysis endpoint returns metrics
- [ ] All metrics within expected ranges

---

## 🐛 Troubleshooting

### Backend Not Responding
1. Check if server is running: `curl http://localhost:8000/api/health`
2. Check port conflicts: `netstat -ano | findstr :8000`
3. Check firewall settings
4. Verify Python environment activated

### CORS Errors
- Backend should have CORS middleware enabled (already configured)
- Check browser console for CORS errors
- Verify backend allows frontend origin

### Connection Timeout
- Check network connectivity
- Verify backend URL in `BackendClientConfig`
- Check backend server logs for errors
- Increase timeout if needed

### Quality Metrics Not Working
- Verify librosa installed: `pip install librosa==0.11.0`
- Check audio file format (WAV, 22050 Hz recommended)
- Verify quality_metrics module imports correctly
- Check backend logs for errors

---

## 📝 Test Results Template

```markdown
## Test Results - [Date]

### Environment
- Backend: Python 3.10.x, FastAPI
- Frontend: WinUI 3, .NET 8
- OS: Windows 11

### Test Results
- Health Check: ✅ Pass
- Profile Management: ✅ Pass
- Project Management: ✅ Pass
- Voice Synthesis: ✅ Pass
- Quality Metrics: ✅ Pass
- Error Handling: ✅ Pass
- Performance: ✅ Pass

### Issues Found
- None

### Notes
- All tests passed successfully
```

---

## 🎯 Success Criteria

**Integration is successful when:**
- ✅ All CRUD operations work end-to-end
- ✅ Quality metrics are calculated and returned
- ✅ Error handling is graceful
- ✅ Performance is acceptable
- ✅ No crashes or data loss
- ✅ UI remains responsive

---

**This guide will be updated as new features are added and tested.**

