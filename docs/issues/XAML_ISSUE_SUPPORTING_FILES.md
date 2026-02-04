# VoiceStudio XAML Compilation Issue - Supporting Files

**Date**: 2026-02-01
**Related**: See `XAML_ISSUE_KEY_FILES.md` for the core problem description

---

## File 1: Directory.Build.props (SDK version and XAML compiler wrapper config)

```xml
<Project>
  <!-- XAML compilation is enabled (per plan: make XAML compilation succeed normally) -->
  <!-- NOTE: Target overrides are in Directory.Build.targets to ensure they run AFTER NuGet imports -->

  <!-- XAML compiler routing (VS-0035 fix) -->
  <!-- Use the WinUI XamlCompiler executable via our wrapper to avoid WMC9999 in-process failures -->
  <!-- See: https://github.com/microsoft/microsoft-ui-xaml/issues/9813 -->
  <PropertyGroup Condition="'$(MSBuildProjectName)' == 'VoiceStudio.App'">
    <UseXamlCompilerExecutable>true</UseXamlCompilerExecutable>
    <!-- Route Exec to repo-local wrapper for better diagnostics + false-positive exit code handling -->
    <XamlCompilerExePath>$(MSBuildThisFileDirectory)tools\xaml-compiler-wrapper.cmd</XamlCompilerExePath>
  </PropertyGroup>

  <!-- Force WinAppSDK version to override transitive dependencies -->
  <PropertyGroup>
    <!-- Allow ad-hoc overrides (e.g., try preview/servicing without editing files) -->
    <MicrosoftWindowsAppSDKVersion Condition="'$(WinAppSdkVersionOverride)' != ''">
      $(WinAppSdkVersionOverride)</MicrosoftWindowsAppSDKVersion>
    <MicrosoftWindowsAppSDKVersion Condition="'$(WinAppSdkVersionOverride)' == ''">1.8.251106002</MicrosoftWindowsAppSDKVersion>
  </PropertyGroup>

  <!-- Package version overrides to ensure consistent versions -->
  <ItemGroup>
    <PackageVersion Include="Microsoft.WindowsAppSDK" Version="$(MicrosoftWindowsAppSDKVersion)" />
    <PackageVersion Include="Microsoft.WindowsAppSDK.WinUI"
      Version="$(MicrosoftWindowsAppSDKVersion)" />
    <PackageDownload Include="Microsoft.WindowsAppSDK.Runtime"
      Version="[$(MicrosoftWindowsAppSDKVersion)]" />
    <PackageVersion Include="CommunityToolkit.WinUI.UI.Controls" Version="7.1.2" />
    <PackageVersion Include="CommunityToolkit.Mvvm" Version="8.2.2" />
    <PackageVersion Include="NAudio" Version="2.2.1" />
    <PackageVersion Include="Microsoft.Windows.SDK.BuildTools" Version="10.0.26100.4654" />
  </ItemGroup>
</Project>
```

---

## File 2: tools/xaml-compiler-wrapper.cmd (custom XAML compiler with diagnostics)

This wrapper exists because of known WinUI XAML compiler issues (VS-0035, WMC9999).

```batch
@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Args: <input.json> <output.json>
set "INPUT_JSON=%~1"
set "OUTPUT_JSON=%~2"

for %%d in ("%~dp0..") do set "REPO_ROOT=%%~fd"
set "APP_ROOT=%REPO_ROOT%\src\VoiceStudio.App"

rem Normalize accidental double backslashes FIRST (can break path existence checks)
set "INPUT_JSON=!INPUT_JSON:\\=\!"
set "OUTPUT_JSON=!OUTPUT_JSON:\\=\!"

rem Normalize to absolute paths relative to app root
if not exist "!INPUT_JSON!" if exist "%APP_ROOT%\!INPUT_JSON!" set "INPUT_JSON=%APP_ROOT%\!INPUT_JSON!"

set "DEBUG_LOG=e:\VoiceStudio\.cursor\debug.log"
set "LOG_RUN_ID=pre-fix"
set "VSQ_DEBUG_ENABLED=0"
if /i "%VSQ_XAML_DEBUG%"=="1" set "VSQ_DEBUG_ENABLED=1"
set "RAW_LOG_ENABLED=0"
if /i "%VSQ_XAML_RAW_LOG%"=="1" set "RAW_LOG_ENABLED=1"

if not exist "!INPUT_JSON!" (
  echo Xaml compiler error: Input JSON file "%~1" doesn't exist! Resolved as "!INPUT_JSON!".
  exit /b 1
)

rem Avoid stale output.json causing incorrect Compile item lists.
if exist "%OUTPUT_JSON%" del /f /q "%OUTPUT_JSON%" >nul 2>nul

rem NuGet root
if defined NUGET_PACKAGES (
  set "NUGET_ROOT=%NUGET_PACKAGES%"
) else (
  set "NUGET_ROOT=%USERPROFILE%\.nuget\packages"
)

rem Pick latest WinUI tools (prefer net6.0, then net472)
set "COMPILER="
for /f "delims=" %%v in ('dir /b /ad "%NUGET_ROOT%\microsoft.windowsappsdk.winui" 2^>nul ^| sort') do (
  if exist "%NUGET_ROOT%\microsoft.windowsappsdk.winui\%%v\tools\net6.0\XamlCompiler.exe" (
    set "COMPILER=%NUGET_ROOT%\microsoft.windowsappsdk.winui\%%v\tools\net6.0\XamlCompiler.exe"
  ) else if exist "%NUGET_ROOT%\microsoft.windowsappsdk.winui\%%v\tools\net472\XamlCompiler.exe" (
    set "COMPILER=%NUGET_ROOT%\microsoft.windowsappsdk.winui\%%v\tools\net472\XamlCompiler.exe"
  )
)

if not defined COMPILER (
  echo Failed to locate XamlCompiler.exe under "%NUGET_ROOT%\microsoft.windowsappsdk.winui\*\tools\*\".
  exit /b 1
)

echo Running XAML compiler...
echo Compiler: "!COMPILER!"
echo Arguments: "!INPUT_JSON!" "!OUTPUT_JSON!"
echo.

rem Change to project directory so relative paths in input.json resolve correctly
cd /d "%APP_ROOT%"

rem Some environments intermittently fail to materialize output.json due to transient file locks
set "MAX_RETRIES=4"
set "RETRY_DELAY_MS=250"
set "ATTEMPT=1"

:_retry_xaml
if "%RAW_LOG_ENABLED%"=="1" (
  echo [%date% %time%] ATTEMPT=%ATTEMPT% >> "!RAW_LOG!"
  "!COMPILER!" "!INPUT_JSON!" "!OUTPUT_JSON!" >> "!RAW_LOG!" 2>&1
) else (
  "!COMPILER!" "!INPUT_JSON!" "!OUTPUT_JSON!"
)
set "EXIT_CODE=%ERRORLEVEL%"

if "%EXIT_CODE%"=="0" (
  if not exist "%OUTPUT_JSON%" (
    echo XAML compiler reported success but output.json is missing - retrying...
    if %ATTEMPT% LSS %MAX_RETRIES% (
      set /a ATTEMPT+=1
      ping 127.0.0.1 -n 1 -w %RETRY_DELAY_MS% >nul
      goto :_retry_xaml
    )
  )
)

echo.
echo XAML compiler exit code: %EXIT_CODE%

rem VS-0001: Some WinUI/XAML compiler builds return exit code 1 but still
rem generate a valid output.json. Treat that as success to avoid blocking builds.
if "%EXIT_CODE%"=="1" (
  echo Checking if output.json was generated despite exit code 1...
  if exist "%OUTPUT_JSON%" (
    findstr /c:"GeneratedCodeFiles" "%OUTPUT_JSON%" >nul 2>nul
    if "%ERRORLEVEL%"=="0" (
      for %%F in ("%OUTPUT_JSON%") do set "OUT_DIR=%%~dpF"
      if exist "!OUT_DIR!App.g.i.cs" if exist "!OUT_DIR!MainWindow.g.i.cs" (
        echo output.json found - treating as false-positive exit code 1
        exit /b 0
      )
    )
  )
)

if "%RAW_LOG_ENABLED%"=="1" (
  echo XAML compilation failed. Dumping log contents:
  type "!RAW_LOG!"
) else (
  echo XAML compilation failed. Re-run with VSQ_XAML_RAW_LOG=1 to capture a raw log.
)

exit /b %EXIT_CODE%
```

---

## Diagnostic Commands Used

### Binary search to find problematic XAML file:

```powershell
$inputJson = Get-Content "src\VoiceStudio.App\obj\x64\Debug\net8.0-windows10.0.19041.0\win-x64\input.json" -Raw | ConvertFrom-Json
$compiler = "C:\Users\Tyler\.nuget\packages\microsoft.windowsappsdk.winui\1.8.251105000\tools\net472\XamlCompiler.exe"
Set-Location "E:\VoiceStudio\src\VoiceStudio.App"

# Test each file individually
foreach ($file in $inputJson.XamlPages) {
    $testInput = $inputJson.PSObject.Copy()
    $testInput.XamlPages = @($file)
    $testInput | ConvertTo-Json -Depth 10 | Set-Content "E:\VoiceStudio\xaml_input_single.json"
    & $compiler "E:\VoiceStudio\xaml_input_single.json" "E:\VoiceStudio\xaml_output_single.json" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        "FAIL: $($file.ItemSpec)"
    }
}
```

**Result**: `Resources\Styles\Controls.xaml` is the file causing the XAML compiler to fail.

### Check Windows Event Log for crash details:

```powershell
Get-WinEvent -FilterHashtable @{LogName='Application'; StartTime=(Get-Date).AddMinutes(-5); Level=2} -MaxEvents 10
```

**Result**:
```
Faulting application name: VoiceStudio.App.exe
Faulting module name: Microsoft.UI.Xaml.dll
Exception code: 0xc000027b
```

---

## Possible Solutions

### Option 1: Load ResourceDictionaries programmatically in App.xaml.cs

Instead of using `ms-appx:///` URIs, load from file paths:

```csharp
protected override void OnLaunched(LaunchActivatedEventArgs args)
{
    var resources = new ResourceDictionary();
    
    // Load from file path instead of ms-appx:///
    var basePath = AppContext.BaseDirectory;
    
    var designTokens = new ResourceDictionary();
    designTokens.Source = new Uri($"file:///{basePath}Resources/DesignTokens.xaml");
    resources.MergedDictionaries.Add(designTokens);
    
    // ... etc
    
    Application.Current.Resources = resources;
}
```

### Option 2: Merge all styles into single ResourceDictionary

Combine DesignTokens.xaml + Controls.xaml + Text.xaml + Panels.xaml into one file so there are no cross-dictionary StaticResource references at compile time.

### Option 3: Use ThemeResource instead of StaticResource

Change `{StaticResource VSQ.Accent.CyanBrush}` to `{ThemeResource VSQ.Accent.CyanBrush}` throughout Controls.xaml. ThemeResource is resolved at runtime, not compile time.

### Option 4: Inline DesignTokens into Controls.xaml

Move all the token definitions that Controls.xaml needs directly into Controls.xaml so it's self-contained.

---

## External References

- https://github.com/microsoft/microsoft-ui-xaml/issues/9813 (WMC9999 XAML compiler failures)
- https://learn.microsoft.com/en-us/windows/apps/winui/winui3/
- https://learn.microsoft.com/en-us/windows/apps/develop/ui-input/xaml-resource-dictionary
- https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/deploy-unpackaged-apps
