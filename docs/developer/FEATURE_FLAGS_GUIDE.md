# Feature Flags Guide

**Phase**: 8.1 Feature Flag System  
**Version**: 1.0.0  
**Last Updated**: 2026-02-05

## Overview

VoiceStudio uses a comprehensive feature flag system for:

- **Gradual rollouts**: Release features to a percentage of users
- **A/B testing**: Run experiments to measure feature impact
- **Kill switches**: Quickly disable problematic features
- **Environment-specific behavior**: Different defaults for dev/staging/prod
- **User segmentation**: Enable features for specific user groups

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Feature Flag System                       │
├─────────────────────────────────────────────────────────────┤
│  Frontend (C#)              │  Backend (Python)              │
│  FeatureFlagsService.cs     │  ab_testing.py                 │
│  - Local flag storage       │  - Experiment management       │
│  - Environment overrides    │  - User bucketing              │
│  - Percentage rollouts      │  - Event tracking              │
│  - A/B test bucketing       │  - Analytics                   │
└─────────────────────────────┴─────────────────────────────────┘
```

## Frontend Usage (C#)

### Basic Flag Checking

```csharp
// Get the service
var featureFlags = App.Current.Services.GetService<IFeatureFlagsService>();

// Check if a feature is enabled
if (featureFlags.IsEnabled("RealTimeQualityMetrics"))
{
    // Feature is enabled
    ShowQualityMetrics();
}
```

### Flag Categories

Flags are organized into categories for better management:

| Category | Purpose | Examples |
|----------|---------|----------|
| `Core` | Essential application features | AnalyticsEnabled, TelemetryEnabled |
| `UI` | User interface features | RealTimeQualityMetrics, CompactUIMode |
| `Backend` | Backend/API features | BackendCachingEnabled, WebSocketEnabled |
| `Experimental` | Features in testing | ExperimentalVoiceMorphing |
| `ABTest` | A/B test variants | ABTest_NewOnboardingFlow |

### Available Flags

#### Core Flags

| Flag | Default | Description |
|------|---------|-------------|
| `HeavyPanelsEnabled` | `true` | Enable heavy panels (Quality Dashboard, Spatial Stage) |
| `AnalyticsEnabled` | `true` | Enable analytics event tracking |
| `PerformanceProfilingEnabled` | `false` | Enable performance profiling and budget monitoring |
| `StressTestMode` | `false` | Enable stress test mode for performance testing |
| `TelemetryEnabled` | `false` | Enable anonymous telemetry collection (opt-in) |

#### UI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `RealTimeQualityMetrics` | `true` | Enable real-time quality metrics display |
| `AdvancedEffectsEnabled` | `true` | Enable advanced audio effects processing |
| `MultiEngineEnsemble` | `true` | Enable multi-engine ensemble synthesis |
| `DarkModeDefault` | `false` | Default to dark mode on first launch |
| `CompactUIMode` | `false` | Enable compact UI mode for smaller screens |

#### Backend Flags

| Flag | Default | Description |
|------|---------|-------------|
| `BackendCachingEnabled` | `true` | Enable backend response caching |
| `WebSocketEnabled` | `true` | Enable WebSocket real-time communication |
| `CircuitBreakerEnabled` | `true` | Enable circuit breaker for engine failures |

#### Experimental Flags (Gradual Rollout)

| Flag | Default | Rollout % | Description |
|------|---------|-----------|-------------|
| `ExperimentalVoiceMorphing` | `false` | 10% | Experimental voice morphing features |
| `ExperimentalStyleTransfer` | `false` | 5% | Experimental style transfer features |
| `ExperimentalRealtimeSynthesis` | `false` | 0% | Experimental real-time synthesis |

### Setting Flags Programmatically

```csharp
// Set a flag value (persisted)
featureFlags.SetFlag("PerformanceProfilingEnabled", true);

// Set an override (highest priority, not persisted)
featureFlags.SetOverride("StressTestMode", true);

// Clear an override
featureFlags.ClearOverride("StressTestMode");
```

### Environment Overrides

Set environment variables to override flags:

```powershell
# Enable a flag via environment variable
$env:VOICESTUDIO_FF_StressTestMode = "true"

# Disable a flag
$env:VOICESTUDIO_FF_AnalyticsEnabled = "false"
```

Environment overrides take highest priority and are useful for:
- CI/CD testing
- Development debugging
- Production emergency overrides

### Subscribing to Flag Changes

```csharp
featureFlags.FlagChanged += (sender, flagName) =>
{
    Console.WriteLine($"Flag changed: {flagName} = {featureFlags.IsEnabled(flagName)}");
    
    // React to flag changes
    if (flagName == "RealTimeQualityMetrics")
    {
        UpdateQualityMetricsVisibility();
    }
};
```

## A/B Testing

### Frontend A/B Testing

```csharp
var featureFlags = App.Current.Services.GetService<FeatureFlagsService>();

// Get A/B test variant
string variant = featureFlags.GetABTestVariant("onboarding_v2");
if (variant == "treatment")
{
    ShowNewOnboarding();
}
else
{
    ShowClassicOnboarding();
}

// Or use the simpler check
if (featureFlags.IsInTreatmentGroup("wizard_simple"))
{
    ShowSimplifiedWizard();
}
```

### Backend A/B Testing (Python)

```python
from backend.services.ab_testing import get_ab_testing_service

ab_service = get_ab_testing_service()

# Create an experiment
experiment = ab_service.create_experiment(
    id="pricing_test",
    name="Pricing Page Test",
    description="Test new pricing layout",
    treatment_weight=50  # 50% get treatment
)

# Start the experiment
ab_service.update_experiment_status("pricing_test", ExperimentStatus.RUNNING)

# Get variant for a user
variant = ab_service.get_variant(user_id, "pricing_test")

# Track exposure (when user sees the variant)
ab_service.track_exposure(user_id, "pricing_test")

# Track conversion
ab_service.track_conversion(user_id, "pricing_test", conversion_value=29.99)

# Get statistics
stats = ab_service.get_experiment_stats("pricing_test")
print(f"Control conversion: {stats['variants'][0]['conversion_rate']}%")
print(f"Treatment conversion: {stats['variants'][1]['conversion_rate']}%")
```

### User Bucketing

Users are assigned to variants using stable hashing:

1. User ID + Experiment ID → SHA256 hash
2. Hash → Bucket (0-99)
3. Bucket compared to variant weights

This ensures:
- **Consistency**: Same user always gets same variant
- **Independence**: Assignment in one experiment doesn't affect others
- **Privacy**: Only hashed IDs are stored

## Percentage Rollouts

Gradual feature rollouts use the same bucketing mechanism:

```csharp
// In FeatureFlagDefinition
AddFlag("NewFeature", true, "New feature with gradual rollout",
    FeatureFlagCategory.Experimental,
    rolloutPercentage: 10);  // Only 10% of users see this
```

### Rollout Strategy

1. **0%**: Feature is disabled for everyone
2. **1-10%**: Internal testing / dogfooding
3. **25%**: Early adopter testing
4. **50%**: Broader testing
5. **100%**: Full rollout

### Monitoring Rollouts

```csharp
// Export current state for debugging
var state = featureFlags.ExportState();
// state contains:
// - userId (for bucket debugging)
// - flags (stored values)
// - overrides (active overrides)
// - effectiveFlags (actual evaluated values)
```

## Remote Configuration

Flags marked as `isRemoteConfigurable` can be synced from a backend:

```csharp
// Enable remote config
featureFlags.SetRemoteConfigEnabled(true);

// Sync from backend
var remoteFlags = await backendClient.GetFeatureFlagsAsync();
await featureFlags.SyncRemoteConfigAsync(remoteFlags);

// Listen for sync events
featureFlags.RemoteConfigSynced += (s, e) =>
{
    Console.WriteLine("Remote flags synced");
};
```

**Note**: Only flags with `IsRemoteConfigurable = true` will be updated.

## Best Practices

### Naming Conventions

```
Category_Feature_Modifier

Examples:
- UI_DarkMode_Default
- Backend_Cache_Enabled
- Experimental_VoiceMorph_V2
- ABTest_Onboarding_NewFlow
```

### Flag Lifecycle

1. **Create**: Add flag with `defaultValue = false`
2. **Test**: Use overrides for development testing
3. **Rollout**: Gradually increase rollout percentage
4. **Stabilize**: Monitor metrics at each rollout level
5. **Graduate**: Set to 100% and `defaultValue = true`
6. **Remove**: Delete flag after code cleanup

### Code Organization

```csharp
// ❌ Bad: Inline flag checks everywhere
if (featureFlags.IsEnabled("NewFeature"))
{
    DoNewThing();
}
else
{
    DoOldThing();
}

// ✅ Good: Encapsulate in a strategy/factory
public ISynthesizer GetSynthesizer()
{
    if (_featureFlags.IsEnabled("ExperimentalRealtimeSynthesis"))
    {
        return new RealtimeSynthesizer();
    }
    return new StandardSynthesizer();
}
```

### Testing with Flags

```csharp
[TestMethod]
public void TestNewFeature_WhenEnabled()
{
    // Arrange
    var featureFlags = new Mock<IFeatureFlagsService>();
    featureFlags.Setup(f => f.IsEnabled("NewFeature")).Returns(true);
    
    // Act & Assert
    // ...
}

[TestMethod]
public void TestNewFeature_WhenDisabled()
{
    var featureFlags = new Mock<IFeatureFlagsService>();
    featureFlags.Setup(f => f.IsEnabled("NewFeature")).Returns(false);
    
    // Act & Assert
    // ...
}
```

## Troubleshooting

### Flag Not Working

1. Check environment overrides: `echo $env:VOICESTUDIO_FF_FlagName`
2. Check stored value: `featureFlags.GetAllFlags()["FlagName"]`
3. Check effective value: `featureFlags.IsEnabled("FlagName")`
4. Check rollout percentage if < 100%

### User Not Getting Expected Variant

1. Verify experiment is `RUNNING`
2. Check user bucket: Use same user ID consistently
3. Verify variant weights add up to 100

### Debug Mode

```csharp
// Export full state for debugging
var state = featureFlags.ExportState();
Console.WriteLine(JsonSerializer.Serialize(state, new JsonSerializerOptions { WriteIndented = true }));
```

## API Reference

### IFeatureFlagsService

| Method | Description |
|--------|-------------|
| `IsEnabled(flag)` | Check if flag is enabled |
| `SetFlag(flag, enabled)` | Set flag value (persisted) |
| `GetAllFlags()` | Get all flag values |
| `GetDescription(flag)` | Get flag description |

### FeatureFlagsService (Extended)

| Method | Description |
|--------|-------------|
| `SetOverride(flag, enabled)` | Set temporary override |
| `ClearOverride(flag)` | Remove override |
| `GetABTestVariant(testId)` | Get "control" or "treatment" |
| `IsInTreatmentGroup(testId)` | Check if user is in treatment |
| `SyncRemoteConfigAsync(flags)` | Sync from remote config |
| `ExportState()` | Export debug state |

### ABTestingService (Python)

| Method | Description |
|--------|-------------|
| `create_experiment(...)` | Create new A/B test |
| `get_variant(user_id, exp_id)` | Get user's variant |
| `track_exposure(...)` | Record variant exposure |
| `track_conversion(...)` | Record conversion event |
| `get_experiment_stats(exp_id)` | Get experiment analytics |

## See Also

- [Architecture Decision Records](../architecture/decisions/)
- [Analytics Guide](./ANALYTICS_GUIDE.md) (Phase 8.2)
- [Quality Automation](./QUALITY_AUTOMATION_GUIDE.md) (Phase 8.3)
