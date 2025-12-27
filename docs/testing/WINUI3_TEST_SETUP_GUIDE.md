# WinUI 3 Test Framework Setup Guide

**Date:** 2025-01-28  
**Status:** Complete  
**Framework:** MSTest 3.4+ with WinUI 3 Support

---

## Overview

This guide provides step-by-step instructions for setting up and configuring the WinUI 3 test framework for VoiceStudio.App.

---

## Prerequisites

### Required Software

- **Visual Studio 2022** (Community or higher) with:
  - .NET 8 SDK
  - Windows 10 SDK (10.0.19041.0 or later)
  - Windows App SDK (1.5.240627000)
- **Windows 10** (1903+) or **Windows 11**

### Verify Prerequisites

```powershell
# Check .NET SDK version
dotnet --version
# Should show 8.0.x or later

# Check Visual Studio installation
# Open Visual Studio Installer and verify:
# - .NET desktop development workload
# - Windows 10 SDK
```

---

## Project Structure

The test project is located at:

```
src/VoiceStudio.App.Tests/
├── ViewModels/          # ViewModel unit tests
├── UI/                  # UI component tests
├── Services/            # Service unit tests
├── Integration/         # Integration tests
├── TestBase.cs          # Base test class
├── App.xaml             # Test app XAML
├── App.xaml.cs          # Test app code-behind
├── GlobalUsings.cs      # Global using statements
└── VoiceStudio.App.Tests.csproj
```

---

## Setup Steps

### Step 1: Verify Test Project Exists

The test project should already be created at:
```
e:\VoiceStudio\src\VoiceStudio.App.Tests\
```

If it doesn't exist, the project structure has been set up with all necessary files.

### Step 2: Add Project References

Edit `VoiceStudio.App.Tests.csproj` and uncomment the project references:

```xml
<ItemGroup>
  <ProjectReference Include="..\VoiceStudio.App\VoiceStudio.App.csproj" />
  <ProjectReference Include="..\VoiceStudio.Core\VoiceStudio.Core.csproj" />
</ItemGroup>
```

**Note:** Ensure the referenced projects exist and build successfully.

### Step 3: Restore NuGet Packages

```powershell
cd e:\VoiceStudio\src\VoiceStudio.App.Tests
dotnet restore
```

Expected packages:
- MSTest.TestFramework (3.4.3)
- MSTest.TestAdapter (3.4.3)
- Microsoft.WindowsAppSDK (1.5.240627000)
- Microsoft.Windows.SDK.BuildTools (10.0.26100.1)

### Step 4: Build Test Project

```powershell
dotnet build
```

Verify the build succeeds without errors.

### Step 5: Verify Test Discovery

Open Visual Studio:
1. Open the solution
2. Build the solution (Ctrl+Shift+B)
3. Open Test Explorer (Test → Test Explorer)
4. Verify tests are discovered

You should see the example test classes:
- `ExampleViewModelTests`
- `ExampleUITests`
- `ExampleServiceTests`
- `ExampleIntegrationTests`

---

## Configuration

### Test Project Settings

The test project is configured with:

- **Target Framework:** `net8.0-windows10.0.19041.0`
- **Platform:** x64
- **Test Framework:** MSTest 3.4.3
- **Code Coverage:** Coverlet collector included

### Test App Configuration

The test project includes `App.xaml` and `App.xaml.cs` which are required for UI tests. These initialize the WinUI 3 application context needed for `[UITestMethod]` tests.

---

## Running Tests

### Visual Studio

1. **Open Test Explorer**
   - Test → Test Explorer (or Ctrl+E, T)

2. **Run All Tests**
   - Click "Run All Tests" button
   - Or right-click → Run All Tests

3. **Run Specific Tests**
   - Right-click on test class/method → Run Tests

4. **View Results**
   - Results appear in Test Explorer
   - Click on test to see details
   - View output in Test Output window

### Command Line

```powershell
# Run all tests
cd e:\VoiceStudio\src\VoiceStudio.App.Tests
dotnet test

# Run with detailed output
dotnet test --logger "console;verbosity=detailed"

# Run specific test class
dotnet test --filter "FullyQualifiedName~ExampleViewModelTests"

# Run with code coverage
dotnet test --collect:"XPlat Code Coverage"
```

### Test Results

Test results are displayed in:
- **Visual Studio:** Test Explorer window
- **Command Line:** Console output
- **Coverage:** `TestResults/` directory (when coverage is enabled)

---

## Writing Tests

### Test Templates

Example test templates are provided in:

- `ViewModels/ExampleViewModelTests.cs` - ViewModel test template
- `UI/ExampleUITests.cs` - UI test template
- `Services/ExampleServiceTests.cs` - Service test template
- `Integration/ExampleIntegrationTests.cs` - Integration test template

### Creating New Tests

1. **Copy a template file**
2. **Rename the file and class**
3. **Update namespace if needed**
4. **Implement test methods**

### Test Naming Convention

Use descriptive names following the pattern:
```
MethodName_Scenario_ExpectedResult
```

Examples:
- `ViewModel_PropertyChange_NotifiesSubscribers`
- `Button_Creation_Succeeds`
- `Service_MethodCall_ReturnsExpectedResult`

### Test Structure (AAA Pattern)

```csharp
[TestMethod]
public void MethodName_Scenario_ExpectedResult()
{
    // Arrange - Set up test data and conditions
    var viewModel = new ExampleViewModel();
    
    // Act - Execute the code under test
    viewModel.SomeProperty = "NewValue";
    
    // Assert - Verify the results
    Assert.AreEqual("NewValue", viewModel.SomeProperty);
}
```

---

## Test Categories

### ViewModel Tests

Use standard `[TestMethod]` for ViewModel tests:

```csharp
[TestClass]
public class ExampleViewModelTests
{
    [TestMethod]
    public void ViewModel_PropertyChange_NotifiesSubscribers()
    {
        // Test implementation
    }
}
```

### UI Component Tests

Use `[UITestMethod]` for UI tests:

```csharp
[TestClass]
public class ExampleUITests
{
    [UITestMethod]
    public void Button_Creation_Succeeds()
    {
        var button = new Button();
        Assert.IsNotNull(button);
    }
}
```

### Service Tests

Use standard `[TestMethod]` for Service tests:

```csharp
[TestClass]
public class ExampleServiceTests
{
    [TestMethod]
    public async Task Service_MethodCall_ReturnsExpectedResult()
    {
        // Test implementation
    }
}
```

### Integration Tests

Use standard `[TestMethod]` for Integration tests:

```csharp
[TestClass]
public class ExampleIntegrationTests
{
    [TestMethod]
    public async Task ViewModel_ServiceIntegration_WorksCorrectly()
    {
        // Test implementation
    }
}
```

---

## Troubleshooting

### Tests Not Discovered

**Problem:** Tests don't appear in Test Explorer

**Solutions:**
1. Ensure project builds successfully
2. Check that test methods have `[TestMethod]` or `[UITestMethod]` attribute
3. Verify test class has `[TestClass]` attribute
4. Rebuild solution (Build → Rebuild Solution)
5. Restart Visual Studio

### UI Tests Fail

**Problem:** `[UITestMethod]` tests fail with UI-related errors

**Solutions:**
1. Verify `App.xaml` and `App.xaml.cs` exist in test project
2. Ensure WinUI 3 packages are properly referenced
3. Check that `[UITestMethod]` attribute is used (not `[TestMethod]`)
4. Verify Windows App SDK is installed

### Project Reference Errors

**Problem:** Build errors about missing project references

**Solutions:**
1. Verify referenced projects exist:
   - `VoiceStudio.App.csproj`
   - `VoiceStudio.Core.csproj`
2. Ensure referenced projects build successfully
3. Check that target frameworks are compatible
4. Restore NuGet packages: `dotnet restore`

### Build Errors

**Problem:** Test project fails to build with RuntimeIdentifier errors

**Note:** This is a known issue with .NET 10 SDK and WindowsAppSDK. Visual Studio typically handles this better than command line.

**Solutions:**
1. **Use Visual Studio** (Recommended): Open the solution in Visual Studio 2022 and build from there
2. **Check .NET SDK version**: `dotnet --version` (should be 8.0+)
3. **Verify Windows SDK is installed**
4. **Restore packages**: `dotnet restore`
5. **Clean and rebuild**: `dotnet clean && dotnet build`
6. **If using .NET 10 SDK**: The RuntimeIdentifier errors are expected and can be ignored if building in Visual Studio works

---

## Best Practices

1. **Use Appropriate Test Attribute**
   - `[TestMethod]` for non-UI tests
   - `[UITestMethod]` only for UI component tests

2. **Keep Tests Isolated**
   - Each test should be independent
   - Don't rely on test execution order
   - Clean up test data in `[TestCleanup]`

3. **Use TestBase**
   - Inherit from `TestBase` for common setup/teardown
   - Override `TestInitialize()` and `TestCleanup()` as needed

4. **Mock Dependencies**
   - Use mocking frameworks (Moq, NSubstitute) for external dependencies
   - Keep tests fast and isolated

5. **Follow AAA Pattern**
   - Arrange: Set up test conditions
   - Act: Execute code under test
   - Assert: Verify results

6. **Write Descriptive Names**
   - Use clear, descriptive test names
   - Follow naming convention: `MethodName_Scenario_ExpectedResult`

---

## Next Steps

1. **Review Test Templates**
   - Examine example test files
   - Understand test structure and patterns

2. **Write First Tests**
   - Start with simple ViewModel tests
   - Progress to UI component tests
   - Add integration tests as needed

3. **Set Up CI/CD**
   - Configure test execution in build pipeline
   - Add code coverage reporting
   - Set up test result publishing

4. **Expand Test Coverage**
   - Add tests for all ViewModels
   - Test all UI components
   - Add integration tests for workflows

---

## Additional Resources

- [MSTest Documentation](https://github.com/microsoft/testfx)
- [Microsoft: WinUI 3 Testing Guide](https://learn.microsoft.com/en-us/windows/apps/winui/winui3/testing/create-winui-unit-test-project)
- [Test Framework Research](./WINUI3_TEST_FRAMEWORK_RESEARCH.md)
- [Test Project README](../../src/VoiceStudio.App.Tests/README.md)

---

**Last Updated:** 2025-01-28  
**Status:** Setup Complete  
**Framework:** MSTest 3.4+ with WinUI 3 Support
