# VoiceStudio.App.Tests

WinUI 3 test project for VoiceStudio.App using MSTest framework.

## Overview

This test project provides comprehensive testing for the VoiceStudio WinUI 3 application, including:

- **Unit Tests**: ViewModels, Services, Models
- **UI Tests**: XAML controls, panels, user interactions (using `[UITestMethod]`)
- **Integration Tests**: Component interactions, backend integration

## Framework

**MSTest 3.4+** - Official Microsoft testing framework with WinUI 3 support.

### Key Features

- `[TestMethod]` - Standard unit tests (non-UI thread)
- `[UITestMethod]` - UI tests that run on the UI thread (for XAML/UI components)
- Built-in test discovery and execution
- Visual Studio Test Explorer integration

## Project Structure

```
VoiceStudio.App.Tests/
├── ViewModels/          # ViewModel unit tests
├── UI/                  # UI component tests (use [UITestMethod])
├── Services/            # Service unit tests
├── Integration/         # Integration tests
├── TestBase.cs          # Base class for common test setup
├── App.xaml             # Test app XAML (required for UI tests)
├── App.xaml.cs          # Test app code-behind
└── GlobalUsings.cs      # Global using statements
```

## Running Tests

### Visual Studio

1. Open Test Explorer (Test → Test Explorer)
2. Build the solution
3. Run all tests or select specific tests

### Command Line

```powershell
# Run all tests
dotnet test

# Run specific test class
dotnet test --filter "FullyQualifiedName~ExampleViewModelTests"

# Run with detailed output
dotnet test --logger "console;verbosity=detailed"

# Run with code coverage
dotnet test --collect:"XPlat Code Coverage"
```

## Writing Tests

### ViewModel Tests

ViewModels can be tested with standard `[TestMethod]` since they don't require UI thread:

```csharp
[TestMethod]
public void ViewModel_PropertyChange_NotifiesSubscribers()
{
    var viewModel = new ExampleViewModel();
    bool propertyChanged = false;
    viewModel.PropertyChanged += (s, e) => propertyChanged = true;
    
    viewModel.SomeProperty = "NewValue";
    
    Assert.IsTrue(propertyChanged);
}
```

### UI Component Tests

UI components must use `[UITestMethod]` to run on the UI thread:

```csharp
[UITestMethod]
public void Button_Creation_Succeeds()
{
    var button = new Button { Content = "Test" };
    Assert.IsNotNull(button);
}
```

### Service Tests

Services can be tested with standard `[TestMethod]`:

```csharp
[TestMethod]
public async Task Service_MethodCall_ReturnsExpectedResult()
{
    var service = new ExampleService();
    var result = await service.SomeMethodAsync();
    Assert.IsNotNull(result);
}
```

## Test Templates

This project includes test templates in:

- `ViewModels/ExampleViewModelTests.cs` - ViewModel test template
- `UI/ExampleUITests.cs` - UI test template
- `Services/ExampleServiceTests.cs` - Service test template
- `Integration/ExampleIntegrationTests.cs` - Integration test template

Copy and modify these templates to create new tests.

## Dependencies

- **MSTest.TestFramework** (3.4.3) - Test framework
- **MSTest.TestAdapter** (3.4.3) - Test adapter for Visual Studio
- **Microsoft.WindowsAppSDK** (1.5.240627000) - WinUI 3 framework
- **VoiceStudio.App** - Main application project (project reference)
- **VoiceStudio.Core** - Core library (project reference)

## Best Practices

1. **Use `[UITestMethod]` only when necessary** - Only for tests that create or interact with XAML/UI elements
2. **Keep tests isolated** - Each test should be independent
3. **Use TestBase** - Inherit from `TestBase` for common setup/teardown
4. **Mock dependencies** - Use mocking frameworks for external dependencies
5. **Test naming** - Use descriptive names: `MethodName_Scenario_ExpectedResult`
6. **Arrange-Act-Assert** - Follow AAA pattern in tests

## Troubleshooting

### Tests not discovered

- Ensure project builds successfully
- Check that test methods have `[TestMethod]` or `[UITestMethod]` attribute
- Verify test class has `[TestClass]` attribute

### UI tests fail

- Ensure `App.xaml` and `App.xaml.cs` exist in test project
- Verify `[UITestMethod]` attribute is used for UI tests
- Check that WinUI 3 packages are properly referenced

### Project reference errors

- Verify `VoiceStudio.App.csproj` and `VoiceStudio.Core.csproj` exist
- Check that projects build successfully
- Ensure target frameworks are compatible

## CI/CD Integration

Tests can be run in CI/CD pipelines:

```yaml
- name: Run Tests
  run: dotnet test --logger "trx;LogFileName=test-results.trx"

- name: Publish Test Results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-results.trx
```

## Code Coverage

Generate code coverage reports:

```powershell
dotnet test --collect:"XPlat Code Coverage" --results-directory:"./TestResults"
```

View coverage reports using tools like:
- Visual Studio Code Coverage
- ReportGenerator
- Coverlet

---

**Last Updated:** 2025-01-28  
**Status:** Ready for Use
