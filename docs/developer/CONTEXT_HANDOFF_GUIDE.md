# Context Handoff Guide

This guide documents the VoiceStudio context handoff system, which enables structured
communication and context transfer between AI agent roles during task execution.

## Overview

The handoff system provides:
- **Validated role transitions** - Ensures handoffs follow valid paths
- **Context preservation** - Maintains continuity across role switches  
- **Escalation protocols** - Defines paths for issue escalation
- **Audit trail** - Records all handoff operations

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Handoff Flow                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Source Role    Handoff Payload    Validation    Target Role        │
│  ┌─────────┐   ┌──────────────┐   ┌──────────┐   ┌─────────┐       │
│  │ Role A  │──▶│  • reason    │──▶│ Protocol │──▶│ Role B  │       │
│  │         │   │  • context   │   │ Validator│   │         │       │
│  │         │   │  • artifacts │   │          │   │         │       │
│  └─────────┘   │  • blockers  │   └──────────┘   └─────────┘       │
│                └──────────────┘         │                           │
│                                         ▼                           │
│                              ┌──────────────────┐                   │
│                              │  Handoff Queue   │                   │
│                              │  (Persistence)   │                   │
│                              └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Role Transition Matrix

Valid transitions between roles:

| Source Role | Valid Targets |
|---|---|
| Overseer | All roles (coordination hub) |
| System Architect | All implementation roles |
| Build & Tooling | Overseer, Architect, Release, Debug |
| UI Engineer | Overseer, Architect, Core Platform, Debug |
| Core Platform | Overseer, Architect, Engine, Build, Debug |
| Engine Engineer | Overseer, Architect, Core Platform, Debug |
| Release Engineer | Overseer, Build, Debug |
| Debug Agent | All roles (can return after investigation) |

### Invalid Transitions

Some transitions are blocked to maintain proper escalation paths:
- UI Engineer → Engine Engineer (escalate via Architect or Overseer)
- Build & Tooling → UI Engineer (not a direct dependency)

## Handoff Payload Structure

```python
@dataclass
class HandoffPayload:
    source_role: str           # Role initiating handoff
    target_role: str           # Role receiving handoff
    task_id: Optional[str]     # Associated task (TASK-XXXX)
    reason: str                # Why this handoff is needed
    context_summary: str       # Brief context for continuity
    escalation_level: str      # normal | urgent | critical
    artifacts: List[str]       # File paths, logs, evidence
    blockers: List[str]        # Current blockers (critical only)
    metadata: Dict[str, Any]   # Additional structured data
    timestamp: str             # ISO format timestamp
```

## Escalation Levels

### Normal
- Standard handoff for routine work
- Required: source_role, target_role, reason

### Urgent
- Time-sensitive issues requiring prompt attention
- Required: All normal fields + context_summary

### Critical
- Blocking issues affecting multiple systems
- Required: All urgent fields + blockers list

## Usage Examples

### Basic Handoff

```python
from tools.context.core.cross_role_protocol import create_handoff

# Create a handoff from UI to Debug
payload, validation = create_handoff(
    source_role="ui-engineer",
    target_role="debug-agent",
    reason="Button component crashes on click in VoiceBrowserView",
    task_id="TASK-0042",
    context_summary="The Select button in voice browser throws NullReferenceException",
    artifacts=["logs/ui_crash.txt", "screenshots/error_dialog.png"],
)

if validation.is_valid:
    # Proceed with handoff
    handoff_queue.push(payload)
else:
    print("Validation errors:", validation.errors)
```

### Validate Before Handoff

```python
from tools.context.core.cross_role_protocol import validate_transition

# Check if transition is valid before creating payload
result = validate_transition("core-platform", "engine-engineer")

if result.is_valid:
    print("Transition allowed")
    for warning in result.warnings:
        print(f"  Warning: {warning}")
else:
    print("Transition blocked:", result.errors)
    for suggestion in result.suggestions:
        print(f"  Suggestion: {suggestion}")
```

### Get Escalation Path

```python
from tools.context.core.cross_role_protocol import get_escalation_path

# Get recommended path for a build failure
path = get_escalation_path("ui-engineer", "build_failure")
# Returns: ['debug-agent', 'build-tooling', 'overseer']

# Follow the path for escalation
for next_role in path:
    if can_resolve_with(next_role):
        handoff_to(next_role)
        break
```

### Urgent Escalation

```python
payload, validation = create_handoff(
    source_role="release-engineer",
    target_role="overseer",
    reason="Production deployment blocked by certificate expiry",
    context_summary="SSL cert expired during deployment, rollback initiated",
    escalation_level="urgent",
    blockers=["cert_renewal_pending"],
    artifacts=["deploy/rollback.log"],
)
```

## Integration with Context System

### Handoff with Context Bundle

When handing off, include context for the receiving role:

```python
from tools.context.core.manager import ContextManager
from tools.context.core.models import AllocationContext

# Generate context for target role
manager = ContextManager.from_config()
context = manager.allocate(AllocationContext(
    task_id="TASK-0042",
    role="debug-agent",  # Target role
    phase="Debug",
))

# Include in handoff
payload.metadata["context_bundle"] = context.to_json()
```

### Handoff Queue

The `HandoffQueue` in `tools/context/core/models.py` provides persistence:

```python
from tools.context.core.models import HandoffQueue, HandoffItem

queue = HandoffQueue()

# Push a handoff
item = HandoffItem(
    source_role="ui-engineer",
    target_role="debug-agent",
    task_id="TASK-0042",
    severity="high",
    summary="Component crash needs investigation",
)
queue.push(item)

# Pop for processing
next_item = queue.pop_for_role("debug-agent")
```

## Error Handling

### Validation Failures

Always check validation before executing handoffs:

```python
payload, validation = create_handoff(...)

if not validation.is_valid:
    # Log errors
    for error in validation.errors:
        logger.error(f"Handoff validation failed: {error}")
    
    # Consider suggestions
    for suggestion in validation.suggestions:
        logger.info(f"Suggestion: {suggestion}")
    
    # Do not proceed with invalid handoff
    raise HandoffValidationError(validation.errors)
```

### Missing Context

If context is incomplete:

```python
if not payload.context_summary and payload.escalation_level != "normal":
    validation.add_warning(
        "Context summary recommended for urgent/critical handoffs"
    )
```

## Best Practices

### 1. Always Include Context Summary

Even for normal handoffs, include context to help the receiving role:

```python
# Good
reason="Build failing in CI pipeline",
context_summary="MSBuild returns error CS0234 in VoiceMorphView.xaml.cs line 42"

# Bad
reason="Build broken"  # No context provided
```

### 2. Reference Specific Artifacts

Include paths to logs, screenshots, or code locations:

```python
artifacts=[
    "logs/build_20260205.txt",
    "src/VoiceStudio.App/Views/Panels/VoiceMorphView.xaml:42",
]
```

### 3. Use Correct Escalation Level

- **Normal**: Routine work transitions
- **Urgent**: Time-sensitive but not blocking
- **Critical**: Blocking issues requiring immediate attention

### 4. Follow Escalation Paths

Use `get_escalation_path()` to find the right recipient:

```python
path = get_escalation_path(current_role, issue_type)
target_role = path[0] if path else "overseer"
```

### 5. Validate Before Execute

Always validate transitions before attempting handoffs:

```python
result = validate_transition(source, target)
if result.is_valid:
    # Proceed
    pass
elif result.warnings:
    # Log warnings but proceed
    logger.warning(f"Handoff warnings: {result.warnings}")
else:
    # Block on errors
    raise InvalidTransitionError(result.errors)
```

## CLI Tools

### Check Valid Targets

```bash
python -c "from tools.context.core.cross_role_protocol import get_valid_targets; print(get_valid_targets('ui-engineer'))"
```

### Get Escalation Path

```bash
python -c "from tools.context.core.cross_role_protocol import get_escalation_path; print(get_escalation_path('core-platform', 'build_failure'))"
```

## Related Documentation

- [Cross-Role Protocol Module](../../tools/context/core/cross_role_protocol.py)
- [Debug Role Integration Guide](DEBUG_ROLE_INTEGRATION_GUIDE.md)
- [Overseer Issue System](OVERSEER_ISSUE_SYSTEM.md)
- [Context Manager](../../tools/context/core/manager.py)
