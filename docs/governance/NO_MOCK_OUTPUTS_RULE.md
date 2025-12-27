# No Mock Outputs or Placeholder Code - Enforcement Rule
## VoiceStudio Quantum+ - Real Implementation Requirement

**Status:** 🚨 **CRITICAL RULE - MANDATORY - HIGHEST PRIORITY**  
**Applies To:** All Cursor Agents, All Code, All Documentation  
**Enforcement:** Overseer + Self-Verification + Automated Checks  
**Priority:** Highest - Blocks task completion, blocks commits, blocks releases  
**Related:** 
- `COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md` - **COMPREHENSIVE RULE** with ALL forbidden terms
- `NO_STUBS_PLACEHOLDERS_RULE.md` - Summary rule

---

## 🚨 Rule Summary

All Cursor agents must write **complete, real code** with working logic — no mock data, placeholders, stubs, or speculative interfaces unless explicitly instructed.

---

## ❌ Must Avoid

**🚫 Do NOT generate (see comprehensive rule for complete list):**

**Bookmarks:**
- ❌ `TODO`, `FIXME`, `NOTE`, `HACK`, `REMINDER`, `XXX`, `WARNING`, `CAUTION`, `BUG`, `ISSUE`, `REFACTOR`, `OPTIMIZE`, `REVIEW`, `CHECK`, `VERIFY`, `TEST`, `DEBUG`, `DEPRECATED`, `OBSOLETE`
- ❌ Any comment indicating incomplete work

**Placeholders:**
- ❌ `throw new NotImplementedException()` (C#), `NotImplementedError` (Python)
- ❌ `return {"mock": true}` or fake responses
- ❌ `return {}`, `return []`, `return null` without implementation
- ❌ Comments saying "placeholder", "dummy", "mock", "fake", "sample", "temporary"
- ❌ Hardcoded filler data

**Stubs:**
- ❌ `pass`-only stubs (Python)
- ❌ Empty class/function shells with no logic
- ❌ Methods that return null/empty without implementation
- ❌ Functions that just return without doing anything

**Tags:**
- ❌ `#TODO`, `#FIXME`, `#PLACEHOLDER`, `#HACK`, `#NOTE`
- ❌ `[IN PROGRESS]`, `[PENDING]`, `[TO BE DONE]`, `[WIP]`

**Status Words/Phrases:**
- ❌ "pending", "incomplete", "unfinished", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "needs", "requires", "missing", "WIP", "tbd", "tba", "tbc"
- ❌ "to be done", "will be implemented", "coming soon", "not yet", "eventually", "later", "for now", "temporary", "in progress", "under development", "work in progress"

**Other:**
- ❌ Unimplemented data flows ("assume this works")
- ❌ Mock protocols or fake API responses
- ❌ Speculative implementations

**📋 COMPLETE LIST:** See `docs/governance/COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md` for exhaustive list of ALL forbidden terms, patterns, synonyms, and variations.

---

## ✅ Required Output Format

**Agents must:**

- ✅ Implement full function bodies, classes, or components
- ✅ Wire UI and backend code together with real bindings or API calls
- ✅ Return real values, real file I/O, real API wiring — not mock protocols
- ✅ If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional and log its usage
- ✅ Use real engine routers, MCPs, or models
- ✅ Perform actual operations (e.g., saving audio, applying effects)
- ✅ Connect UI panels to real data sources
- ✅ Make real API calls to backend services

---

## 🔍 Completion Criteria

**Functionality must be:**

- ✅ **Verifiable and testable** - Can be tested with real inputs
- ✅ **UI panels display actual values** - Connected to real models, MCPs, or engine routers
- ✅ **Backend code performs intended operations** - Actually saves audio, applies effects, etc.
- ✅ **No component marked complete** if its implementation is speculative or empty
- ✅ **Real data flows** - No "assume this works" comments
- ✅ **Production-ready** - Can be used in real scenarios

---

## 👮 Overseer Tasks

**The Overseer agent must:**

- ✅ **Reject mock-only modules** - Flag any code with mock outputs
- ✅ **Flag any output containing `TODO`, `mock`, or hardcoded filler** as incomplete
- ✅ **Approve only full-functionality commits** - Verify real implementations
- ✅ **Encourage reuse of shared libraries** or hooks to reduce boilerplate
- ✅ **Verify UI-backend connections** are real, not mocked
- ✅ **Check for real API calls** instead of fake responses

---

## 📝 Examples

### ❌ BAD (Mock Output):

```python
def generate_audio(voice_id):
    # TODO: implement
    return {"mock_audio": true}
```

```csharp
public async Task<AudioResult> SynthesizeAsync(string text)
{
    // TODO: Implement synthesis
    return new AudioResult { Mock = true };
}
```

```python
def get_profiles():
    pass  # TODO: implement
```

```csharp
public List<Profile> GetProfiles()
{
    // Placeholder
    return new List<Profile> { new Profile { Name = "Mock Profile" } };
}
```

### ✅ GOOD (Real Implementation):

```python
def generate_audio(voice_id: str, text: str) -> dict:
    """Generate audio using real engine."""
    engine = router.get_engine("xtts_v2")
    result = engine.synthesize(
        text=text,
        voice_id=voice_id,
        language="en"
    )
    return {
        "audio_path": result.audio_path,
        "duration": result.duration,
        "quality_metrics": result.quality_metrics
    }
```

```csharp
public async Task<AudioResult> SynthesizeAsync(string text)
{
    var engine = _engineRouter.GetEngine("xtts_v2");
    var result = await engine.SynthesizeAsync(text, _currentVoiceProfile);
    
    return new AudioResult
    {
        AudioPath = result.AudioPath,
        Duration = result.Duration,
        QualityMetrics = result.QualityMetrics
    };
}
```

```python
def get_profiles() -> List[Profile]:
    """Load profiles from backend API."""
    response = requests.get(f"{BACKEND_URL}/api/profiles")
    response.raise_for_status()
    return [Profile.from_dict(p) for p in response.json()]
```

```csharp
public async Task<List<Profile>> GetProfilesAsync()
{
    var response = await _httpClient.GetAsync("/api/profiles");
    response.EnsureSuccessStatusCode();
    var profiles = await response.Content.ReadFromJsonAsync<List<ProfileDto>>();
    return profiles.Select(p => Profile.FromDto(p)).ToList();
}
```

### ✅ GOOD (Test Mode Exception):

```python
def generate_audio(voice_id: str, text: str) -> dict:
    """Generate audio using real engine or test mode."""
    if TEST_MODE:
        logger.info("TEST_MODE: Using mock audio generation")
        return {
            "audio_path": "/test/mock_audio.wav",
            "duration": 5.0,
            "quality_metrics": {"mos": 4.0}
        }
    
    # Real implementation
    engine = router.get_engine("xtts_v2")
    result = engine.synthesize(text=text, voice_id=voice_id, language="en")
    return {
        "audio_path": result.audio_path,
        "duration": result.duration,
        "quality_metrics": result.quality_metrics
    }
```

---

## 🔍 Verification Checklist

Before marking ANY task as complete, verify:

- [ ] **NO mock outputs** in return values
- [ ] **NO `{"mock": true}`** or similar fake responses
- [ ] **NO `pass`-only stubs** (Python)
- [ ] **NO hardcoded filler data**
- [ ] **NO speculative implementations**
- [ ] **Real API calls** to backend services
- [ ] **Real file I/O** operations
- [ ] **Real engine/router connections**
- [ ] **UI connected to real data sources**
- [ ] **All operations perform actual work**
- [ ] **Test mode mocks** (if any) clearly marked and logged

---

## 🚨 Consequences

### If Mock Outputs Found:

1. **Task marked as INCOMPLETE**
2. **Worker must implement real code before moving on**
3. **No credit for mock implementations**
4. **May delay overall timeline**

### Why This Matters:

- **Quality:** Mock code creates false sense of completion
- **Reliability:** Real implementations are testable and verifiable
- **User Experience:** Mock outputs don't work for users
- **Maintainability:** Real code is easier to maintain and debug
- **Professionalism:** Production code must be real and functional

---

## 🎯 Remember

**If it's not real, it's not done.**

**Mock outputs are placeholders, not implementations.**

**Complete functionality requires real code, real connections, real operations.**

---

**This rule applies to ALL Cursor agents, ALL tasks, ALL the time.**

**No exceptions.**

---

## 🔍 Automated Verification

**Run before committing:**

```bash
python tools/verify_non_mock.py
```

This tool automatically scans code for:
- Mock outputs and fake responses
- TODO comments
- Placeholder code
- NotImplementedException
- Empty implementations
- Hardcoded filler data

**See:** `tools/verify_non_mock.py` for complete tool documentation

---

**Last Updated:** 2025-01-28  
**Status:** 🚨 **CRITICAL RULE - ENFORCED**

---

## 📋 COMPREHENSIVE RULE REFERENCE

**For the complete, expanded rule with ALL forbidden terms, patterns, synonyms, and variations, see:**
- `docs/governance/COMPLETE_NO_STUBS_PLACEHOLDERS_BOOKMARKS_RULE.md`

**This comprehensive document includes:**
- Complete list of all forbidden bookmarks, placeholders, stubs, tags, and status words
- All synonyms and variations
- Complete verification checklist
- Examples of bad vs. good code
- Automated enforcement recommendations

