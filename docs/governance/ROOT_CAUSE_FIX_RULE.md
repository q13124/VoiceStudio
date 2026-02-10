# Root Cause Fix Rule

## MANDATORY DEVELOPMENT STANDARD

**Effective Date:** 2024  
**Applies To:** All contributors, AI agents, and automated systems  
**Enforcement Level:** CRITICAL - Violations block merge

---

## Executive Summary

**All code changes MUST address root causes. Workarounds, hacks, temporary fixes, and band-aid solutions are STRICTLY FORBIDDEN.**

This rule ensures long-term code quality, maintainability, and reliability by requiring every fix to address the underlying problem rather than masking symptoms.

---

## The Rule

### Statement

> **Every code change that addresses a bug, issue, or deficiency MUST fix the root cause of the problem. Workarounds that merely suppress symptoms or defer proper resolution are not permitted.**

### Definition of Terms

| Term | Definition |
|------|------------|
| **Root Cause** | The fundamental underlying reason why a problem occurs; the origin point that, when corrected, eliminates the problem permanently |
| **Root Cause Fix** | A code change that directly addresses and corrects the root cause, preventing the problem from recurring |
| **Workaround** | A temporary or partial solution that avoids or masks the problem without addressing its origin |
| **Hack** | An inelegant, non-standard, or undocumented solution that works around system constraints improperly |
| **Band-aid Fix** | A superficial fix that addresses symptoms rather than causes |
| **Technical Debt** | Accumulated cost of choosing expedient solutions over proper ones |

---

## What is FORBIDDEN

### Explicitly Prohibited Patterns

1. **Symptom Suppression**
   - Catching and ignoring exceptions to hide errors
   - Using `try/catch` to swallow problems without resolution
   - Disabling validation to bypass errors

   ```csharp
   // FORBIDDEN: Swallowing exceptions
   try { DoOperation(); }
   catch { } // Silent failure - FORBIDDEN
   
   // FORBIDDEN: Ignoring errors
   catch (Exception) { return null; } // Hiding the problem
   ```

2. **Retry Loops Without Resolution**
   - Retry mechanisms that don't address why operations fail
   - Infinite retry patterns that mask underlying issues

   ```python
   # FORBIDDEN: Blind retry without understanding cause
   for _ in range(100):
       try:
           do_thing()
           break
       except:
           time.sleep(1)  # Just hoping it works eventually
   ```

3. **Magic Numbers and Arbitrary Delays**
   - Adding `Thread.Sleep()` or `await Task.Delay()` to "fix" race conditions
   - Arbitrary timeout values without addressing timing issues

   ```csharp
   // FORBIDDEN: Using delay to mask race condition
   await Task.Delay(500); // "This fixes the crash"
   DoOperation();
   ```

4. **Conditional Bypasses**
   - Adding `if` statements to skip problematic code paths
   - Feature flags used to permanently disable broken functionality

   ```python
   # FORBIDDEN: Bypassing instead of fixing
   if not is_broken_feature_enabled:
       skip_processing()  # Just avoiding the problem
   ```

5. **Data Manipulation to Avoid Errors**
   - Modifying input data to prevent crashes instead of handling it properly
   - Truncating, filtering, or transforming data to work around bugs

   ```csharp
   // FORBIDDEN: Data manipulation to avoid crash
   var safeInput = input.Replace("problematic", ""); // Hiding the issue
   ```

6. **Version Pinning Without Resolution**
   - Pinning dependencies to avoid bugs without addressing compatibility
   - Downgrading packages as a permanent solution

   ```
   # FORBIDDEN: Permanent downgrade without resolution plan
   numpy==1.26.4  # "New version crashes, just use old one forever"
   ```

7. **Disabling Tests**
   - Skipping or deleting tests that fail instead of fixing the code
   - Adding `[Ignore]` or `@pytest.mark.skip` to avoid failures

   ```csharp
   // FORBIDDEN: Disabling tests to hide failures
   [Ignore("Flaky test, will fix later")]  // Permanent ignore
   public void TestThatFails() { }
   ```

8. **Environment-Specific Workarounds**
   - Code that only works in certain environments
   - Production-specific hacks

   ```python
   # FORBIDDEN: Environment hack
   if os.environ.get("PRODUCTION"):
       use_workaround()  # Only works in production
   ```

---

## What is REQUIRED

### Root Cause Analysis Process

Before implementing any fix:

1. **Identify the Symptom**
   - What is the observable problem?
   - When does it occur?
   - What are the conditions?

2. **Trace to Root Cause**
   - Why does this symptom occur?
   - What is the underlying cause?
   - Keep asking "why" until you reach the fundamental issue

3. **Verify Root Cause**
   - Can you reproduce the issue consistently?
   - Does addressing this cause eliminate all symptoms?
   - Are there other symptoms from the same root cause?

4. **Design Proper Fix**
   - What is the correct solution at the root level?
   - Does it follow architectural patterns?
   - Is it maintainable and testable?

5. **Implement and Validate**
   - Implement the fix at the root level
   - Write tests that verify the root cause is addressed
   - Ensure no regressions

### Proper Fix Patterns

**Example 1: Race Condition**

```csharp
// WRONG: Delay workaround
await Task.Delay(500);
DoOperation();

// CORRECT: Proper synchronization
await _semaphore.WaitAsync();
try
{
    await DoOperationAsync();
}
finally
{
    _semaphore.Release();
}
```

**Example 2: Null Reference**

```csharp
// WRONG: Null check workaround
if (obj != null)
    obj.DoThing(); // Hiding that obj should never be null

// CORRECT: Fix the source
// Find WHY obj is null and fix initialization
public MyClass()
{
    _obj = new RequiredDependency(); // Proper initialization
}
```

**Example 3: API Compatibility**

```python
# WRONG: Version pin workaround
# requirements.txt: numpy==1.26.4  # Old version forever

# CORRECT: Proper compatibility fix
# 1. Identify incompatible API calls
# 2. Update code to use compatible APIs
# 3. Add compatibility layer if needed
import numpy as np
# Use np.asarray() instead of deprecated np.array() behavior
```

**Example 4: Error Handling**

```python
# WRONG: Swallow exception
try:
    process_data(data)
except Exception:
    pass  # Ignore all errors

# CORRECT: Handle appropriately
try:
    process_data(data)
except ValidationError as e:
    logger.warning(f"Invalid data: {e}")
    raise UserFacingError("Please provide valid input") from e
except ProcessingError as e:
    logger.error(f"Processing failed: {e}")
    raise ServiceError("Processing unavailable") from e
```

---

## Enforcement

### Code Review Requirements

All pull requests MUST include:

1. **Root Cause Statement**
   - Clear description of the root cause identified
   - Explanation of how the fix addresses it

2. **No Workaround Attestation**
   - Explicit statement that the change contains no workarounds
   - Reviewer verification of this claim

3. **Test Coverage**
   - Tests that verify the root cause is fixed
   - Tests that would fail if the problem recurs

### Pull Request Template Addition

```markdown
## Root Cause Analysis

### Problem Description
[What is the observable issue?]

### Root Cause Identified
[What is the fundamental cause of this issue?]

### How This Fix Addresses Root Cause
[Explain how your changes fix the underlying problem]

### Workaround Attestation
- [ ] This change contains NO workarounds, hacks, or band-aid fixes
- [ ] This change addresses the root cause, not symptoms
- [ ] Tests verify the root cause is resolved
```

### Automated Checks

The CI/CD pipeline checks for:

1. **Prohibited Patterns**
   - Empty catch blocks
   - `Thread.Sleep` / `Task.Delay` without justification
   - `[Ignore]` / `@skip` without approved exception
   - TODO comments without linked issues

2. **Required Elements**
   - Root cause documentation in PR description
   - Test coverage for the fix
   - No regression in test suite

---

## Exceptions Process

### When Exceptions May Be Considered

Exceptions are RARE and require:

1. **Critical Production Emergency**
   - System is down or severely impacted
   - Immediate mitigation required
   - Proper fix cannot be implemented within emergency window

2. **Exception Requirements**
   - Written approval from project lead
   - Linked tracking issue for proper fix
   - Defined timeline for proper resolution (max 2 weeks)
   - Workaround clearly marked with `// TEMPORARY WORKAROUND - Issue #XXX`

3. **Exception Documentation**

   ```csharp
   // TEMPORARY WORKAROUND - Issue #1234
   // Root Cause: Race condition in audio processing pipeline
   // Proper Fix: Implement proper synchronization (PR pending)
   // Deadline: 2024-02-15
   // Approved By: [Lead Name]
   await Task.Delay(100); // REMOVE after proper fix
   ```

### Exception Tracking

All exceptions are tracked in:
- `docs/governance/TECH_DEBT_REGISTER.md`
- GitHub Issues with `workaround-exception` label
- Sprint planning for timely resolution

---

## Rationale

### Why This Rule Exists

1. **Long-term Maintainability**
   - Workarounds accumulate into unmaintainable code
   - Root cause fixes prevent problem recurrence
   - Clean code is easier to understand and modify

2. **Reliability**
   - Workarounds often fail under edge cases
   - Root cause fixes provide comprehensive solutions
   - System stability improves over time

3. **Developer Productivity**
   - Time spent on workarounds is wasted
   - Root cause fixes eliminate repeated debugging
   - Clear code requires less onboarding time

4. **Technical Debt Prevention**
   - Workarounds create hidden debt
   - Debt accumulates interest (more bugs, slower development)
   - Prevention is cheaper than remediation

### Cost of Workarounds

| Approach | Initial Time | Maintenance Time | Total Cost (1 year) |
|----------|-------------|------------------|---------------------|
| Workaround | 1 hour | 10+ hours debugging, explaining, re-fixing | 11+ hours |
| Root Cause Fix | 4 hours | 0 hours | 4 hours |

---

## Integration with Other Standards

This rule works alongside:

- **[NO_STUBS_PLACEHOLDERS_RULE.md](NO_STUBS_PLACEHOLDERS_RULE.md)** - All code must be complete
- **[DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)** - Acceptance criteria for completion
- **[CODE_REVIEW_CHECKLIST.md](../developer/CODE_REVIEW_CHECKLIST.md)** - Review requirements
- **[TECH_DEBT_REGISTER.md](TECH_DEBT_REGISTER.md)** - Tracking technical debt

---

## Summary

| DO | DON'T |
|----|-------|
| Investigate root cause | Apply quick fixes without understanding |
| Fix the underlying problem | Mask symptoms with workarounds |
| Write tests for the root cause | Disable failing tests |
| Document your analysis | Skip analysis to save time |
| Ask for help understanding issues | Guess and apply band-aids |
| Take time to fix properly | Rush incomplete solutions |

---

## Acknowledgment

All contributors must acknowledge understanding of this rule before contributing code.

**By contributing to this project, you agree to:**
1. Investigate root causes before implementing fixes
2. Never submit workarounds as permanent solutions
3. Document your root cause analysis
4. Accept review feedback about workaround patterns
5. Fix identified workarounds when found

---

*This rule is enforced through code review, automated checks, and team accountability. Violations will be rejected during review.*
