# VoiceStudio Quantum+ - Cursor Agent Guidelines
## Direct Guidelines for All Cursor Agents

**Last Updated:** 2025-01-27  
**Purpose:** Essential rules and guidelines for all Cursor agents working on VoiceStudio Quantum+

---

## 🚨 CRITICAL: No Mock Outputs or Placeholder Code

### Rule Summary

All Cursor agents must write **complete, real code** with working logic — no mock data, placeholders, stubs, or speculative interfaces unless explicitly instructed.

### Must Avoid

**🚫 Do NOT generate:**

- `TODO` comments
- `pass`-only stubs
- `return {"mock": true}` or fake responses
- Empty class/function shells with no logic
- Unimplemented data flows ("assume this works")
- Mock protocols or fake API responses
- Hardcoded filler data
- Speculative implementations

### Required Output Format

**✅ Agents must:**

- Implement full function bodies, classes, or components
- Wire UI and backend code together with real bindings or API calls
- Return real values, real file I/O, real API wiring — not mock protocols
- If mocking is required for testing, wrap it in a clear `if TEST_MODE:` conditional and log its usage
- Use real engine routers, MCPs, or models
- Perform actual operations (e.g., saving audio, applying effects)

### Completion Criteria

**Functionality must be:**

- Verifiable and testable
- UI panels display actual values or connect to real models, MCPs, or engine routers
- Backend code performs its intended effect or operation
- No component marked complete if its implementation is speculative or empty

### Overseer Tasks

**The Overseer agent must:**

- Reject mock-only modules
- Flag any output containing `TODO`, `mock`, or hardcoded filler as incomplete
- Approve only full-functionality commits
- Encourage reuse of shared libraries or hooks to reduce boilerplate

### Examples

#### ❌ BAD (Mock Output):

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

#### ✅ GOOD (Real Implementation):

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

---

## 🔍 Verification Tool

**Run before committing:**

```bash
# Check all code
python tools/verify_non_mock.py

# Check specific directory
python tools/verify_non_mock.py --path backend/

# Strict mode (fails on warnings too)
python tools/verify_non_mock.py --strict
```

**This tool automatically checks for:**
- ✅ Mock outputs (`return {"mock": true}`)
- ✅ TODO comments
- ✅ Placeholder code (`[PLACEHOLDER]`)
- ✅ NotImplementedException
- ✅ Empty implementations (`pass`-only stubs)
- ✅ "Coming soon" messages
- ✅ Hardcoded filler data

**Output:**
- ✅ Shows file, line number, and issue type
- ✅ Groups by severity (errors vs warnings)
- ✅ Exits with code 1 if issues found (for CI/CD)

**See:** `tools/verify_non_mock.py` for complete tool documentation

---

## 📚 Additional Resources

- **Complete Rules:** `docs/governance/ALL_PROJECT_RULES.md`
- **No Mock Outputs Rule:** `docs/governance/NO_MOCK_OUTPUTS_RULE.md`
- **No Stubs Rule:** `docs/governance/NO_STUBS_PLACEHOLDERS_RULE.md`
- **Code Improvement Example:** `docs/governance/CODE_IMPROVEMENT_EXAMPLE.md`

---

**Remember: If it's not real, it's not done. Mock outputs are placeholders, not implementations.**

---

**Last Updated:** 2025-01-27  
**Status:** 🚨 **CRITICAL - ENFORCED**

