# No Stubs or Placeholders Rule

## MANDATORY DEVELOPMENT STANDARD

**Effective Date:** 2024  
**Applies To:** All contributors, AI agents, and automated systems  
**Enforcement Level:** CRITICAL - Violations block merge

---

## Executive Summary

**All code MUST be 100% complete and functional. Stubs, placeholders, TODO comments, and incomplete implementations are STRICTLY FORBIDDEN.**

This rule ensures every contribution is production-ready and provides immediate value without requiring follow-up work.

---

## The Rule

### Statement

> **Every line of code committed to this repository must be complete, functional, tested, and documented. No stub implementations, placeholder values, or deferred work is permitted.**

---

## What is FORBIDDEN

### 1. TODO Comments

```csharp
// FORBIDDEN
// TODO: Implement this later
// TODO: Add error handling
// FIXME: This is broken
// HACK: Temporary fix
// XXX: Needs review
```

### 2. NotImplementedException

```csharp
// FORBIDDEN
public async Task<Result> ProcessAsync()
{
    throw new NotImplementedException();
}

public string GetValue() => throw new NotImplementedException("Coming soon");
```

### 3. Placeholder Values

```csharp
// FORBIDDEN
private const string ApiKey = "PLACEHOLDER";
private const string Endpoint = "https://example.com/TODO";
private string _description = "[PLACEHOLDER]";
```

### 4. Empty or Stub Methods

```csharp
// FORBIDDEN
public void Initialize()
{
    // Will implement later
}

public async Task SaveAsync()
{
    await Task.CompletedTask; // Stub
}

public bool Validate(string input)
{
    return true; // Always returns true, not real validation
}
```

### 5. Commented-Out Code

```csharp
// FORBIDDEN
public void Process()
{
    // DoStepOne();
    // DoStepTwo();  // Uncomment when ready
    DoStepThree();
}
```

### 6. Incomplete Switch/Case Statements

```csharp
// FORBIDDEN
switch (status)
{
    case Status.Active:
        HandleActive();
        break;
    // TODO: Handle other cases
    default:
        break; // Silently ignores
}
```

### 7. Hardcoded Test Values in Production Code

```csharp
// FORBIDDEN
public string GetUserId()
{
    return "test-user-123"; // Hardcoded for testing
}
```

### 8. Incomplete Error Messages

```csharp
// FORBIDDEN
throw new Exception("Error"); // Non-descriptive
throw new Exception("TODO: Add proper message");
```

---

## What is REQUIRED

### 1. Complete Implementations

Every method must fully implement its contract:

```csharp
// CORRECT
public async Task<VoiceProfile> GetProfileAsync(string profileId, CancellationToken ct = default)
{
    if (string.IsNullOrWhiteSpace(profileId))
        throw new ArgumentException("Profile ID is required", nameof(profileId));

    var profile = await _backendClient.GetProfileAsync(profileId, ct);
    
    if (profile == null)
        throw new EntityNotFoundException($"Profile '{profileId}' not found");

    return profile;
}
```

### 2. Proper Error Handling

All error paths must be handled:

```csharp
// CORRECT
public async Task<Result> ProcessAsync(Request request, CancellationToken ct)
{
    try
    {
        ValidateRequest(request);
        var result = await ExecuteAsync(request, ct);
        return Result.Success(result);
    }
    catch (ValidationException ex)
    {
        _logger.LogWarning(ex, "Validation failed for request {RequestId}", request.Id);
        return Result.Failure(ex.Message);
    }
    catch (OperationCanceledException) when (ct.IsCancellationRequested)
    {
        _logger.LogInformation("Operation cancelled for request {RequestId}", request.Id);
        throw;
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Unexpected error processing request {RequestId}", request.Id);
        return Result.Failure("An unexpected error occurred");
    }
}
```

### 3. Complete Switch Statements

All cases must be handled:

```csharp
// CORRECT
switch (status)
{
    case Status.Active:
        return HandleActive();
    case Status.Pending:
        return HandlePending();
    case Status.Inactive:
        return HandleInactive();
    case Status.Deleted:
        return HandleDeleted();
    default:
        throw new InvalidOperationException($"Unknown status: {status}");
}
```

### 4. Descriptive Error Messages

All errors must provide actionable information:

```csharp
// CORRECT
throw new InvalidOperationException(
    $"Cannot synthesize audio: Profile '{profileId}' has no voice model configured. " +
    $"Please configure a voice model in the profile settings.");
```

### 5. Complete Documentation

All public APIs must be documented:

```csharp
// CORRECT
/// <summary>
/// Synthesizes speech audio from the provided text using the specified voice profile.
/// </summary>
/// <param name="profileId">The unique identifier of the voice profile to use.</param>
/// <param name="text">The text to synthesize (1-10000 characters).</param>
/// <param name="options">Optional synthesis configuration.</param>
/// <param name="cancellationToken">Cancellation token for the operation.</param>
/// <returns>A synthesis result containing the audio ID and quality metrics.</returns>
/// <exception cref="ArgumentException">Thrown when profileId is null/empty or text exceeds limits.</exception>
/// <exception cref="EntityNotFoundException">Thrown when the specified profile does not exist.</exception>
/// <exception cref="SynthesisException">Thrown when audio synthesis fails.</exception>
public async Task<SynthesisResult> SynthesizeAsync(
    string profileId,
    string text,
    SynthesisOptions? options = null,
    CancellationToken cancellationToken = default)
```

---

## Verification Checklist

Before committing code, verify:

- [ ] No TODO, FIXME, HACK, or XXX comments
- [ ] No `throw new NotImplementedException()`
- [ ] No placeholder strings like "[PLACEHOLDER]", "TODO", "TBD"
- [ ] No empty method bodies (except required interface implementations with proper exceptions)
- [ ] No commented-out code blocks
- [ ] All switch statements handle all cases or throw for unknown
- [ ] All error messages are descriptive and actionable
- [ ] All public methods have XML documentation
- [ ] All code paths have appropriate error handling
- [ ] All tests pass and cover new functionality

---

## Automated Detection

The CI/CD pipeline automatically scans for:

| Pattern | Detection Method |
|---------|-----------------|
| TODO/FIXME comments | Regex scan |
| NotImplementedException | Static analysis |
| Placeholder strings | Pattern matching |
| Empty catch blocks | Code analysis |
| Missing documentation | Documentation coverage |
| Incomplete tests | Coverage thresholds |

---

## Relationship to Root Cause Fix Rule

This rule complements the [ROOT_CAUSE_FIX_RULE.md](ROOT_CAUSE_FIX_RULE.md):

- **No Stubs Rule**: Code must be complete
- **Root Cause Rule**: Code must correctly solve the actual problem

Both rules together ensure: **Complete code that correctly addresses root causes.**

---

## Summary

| Complete Code | Incomplete Code (FORBIDDEN) |
|--------------|---------------------------|
| Full implementation | Stub methods |
| Proper error handling | Empty catch blocks |
| All cases handled | Missing switch cases |
| Descriptive messages | Generic errors |
| Documentation | No comments |
| Tested | No tests |

---

*This rule is enforced through code review, automated checks, and team accountability. Violations will be rejected during review.*
