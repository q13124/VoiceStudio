# ADR-030: ViewModel Dependency Injection Migration

## Status

Accepted (2026-02-06)

## Context

VoiceStudio's MVVM architecture initially used a Service Locator pattern for dependency resolution in ViewModels. This created several problems:

1. **Hidden dependencies**: ViewModels resolved services at runtime, making their true dependencies opaque
2. **Testing difficulties**: Mocking services required complex setup with the service locator
3. **Coupling to container**: ViewModels were tightly coupled to the specific IoC container
4. **Initialization order issues**: Services might not be registered when ViewModels were constructed

As the application grew to 95+ panels and numerous services, these issues became more pronounced:
- Null reference exceptions when services weren't registered
- Difficult debugging of dependency chains
- Inconsistent service lifetime management
- Code duplication for service resolution

## Decision

Migrate all ViewModels from Service Locator pattern to Constructor Dependency Injection (DI):

### 1. BaseViewModel Changes

The `BaseViewModel` base class now requires all core services via constructor:

```csharp
public BaseViewModel(
    ToastNotificationService? toastService,
    ErrorDialogService? errorDialogService,
    StatePersistenceService? statePersistenceService,
    OperationQueueService? operationQueueService,
    StateCacheService? stateCacheService,
    GracefulDegradationService? gracefulDegradationService)
{
    ToastService = toastService;
    ErrorDialogService = errorDialogService;
    StatePersistenceService = statePersistenceService;
    OperationQueueService = operationQueueService;
    StateCacheService = stateCacheService;
    GracefulDegradationService = gracefulDegradationService;
}
```

### 2. ViewModel Registration

All ViewModels are registered with the DI container in `App.xaml.cs`:

```csharp
services.AddTransient<LibraryViewModel>();
services.AddTransient<ProfilesViewModel>();
// ... all other ViewModels
```

### 3. View Construction

Views resolve their ViewModels from the container:

```csharp
public LibraryView()
{
    InitializeComponent();
    ViewModel = App.GetService<LibraryViewModel>();
    DataContext = ViewModel;
}
```

### 4. Nullable Services Pattern

Services are marked as nullable to support graceful degradation when running in limited contexts (e.g., tests, design mode):

```csharp
protected ToastNotificationService? ToastService { get; }
```

## Consequences

### Positive

1. **Explicit dependencies**: All ViewModel dependencies are visible in the constructor
2. **Testability**: ViewModels can be instantiated with mock dependencies
3. **Container independence**: Constructor injection works with any DI container
4. **Compile-time verification**: Missing dependencies cause build errors rather than runtime exceptions
5. **IntelliSense support**: Dependencies are discoverable via constructor parameters

### Negative

1. **Migration effort**: All 50+ ViewModels required updates
2. **Larger constructors**: Some ViewModels have many parameters
3. **View complexity**: Views must resolve ViewModels from the container

### Neutral

1. **Service lifetime**: Services must be carefully configured (Singleton vs Transient vs Scoped)
2. **Circular dependencies**: Must be avoided or resolved via factory patterns

## Implementation Notes

### Migration Steps (Completed)

1. Updated `BaseViewModel` to accept services via constructor
2. Removed legacy parameterless constructor
3. Updated all derived ViewModels to pass services to base
4. Registered ViewModels in DI container
5. Updated Views to resolve ViewModels from container
6. Removed Service Locator calls from ViewModels

### Related Patterns

The CQRS pattern used for command execution also benefits from this change:
- Commands receive services via constructor
- Command handlers are registered in DI container
- `UnifiedCommandRegistry` uses DI for handler resolution

### Future Considerations

- Consider using property injection for optional services
- Evaluate Source Generators for reducing boilerplate
- Consider AutoFac or other containers with more advanced features

## Related ADRs

- ADR-008: Architecture Patterns (MVVM foundation)
- ADR-023: UI Assembly Split (service organization)
- ADR-028: Unified Command Architecture (command DI)
