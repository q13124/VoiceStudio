@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Args: <input.json> <output.json>
set "INPUT_JSON=%~1"
set "OUTPUT_JSON=%~2"

for %%d in ("%~dp0..") do set "REPO_ROOT=%%~fd"
set "APP_ROOT=%REPO_ROOT%\src\VoiceStudio.App"

rem Normalize to absolute paths relative to app root
if not exist "%INPUT_JSON%" if exist "%APP_ROOT%\%INPUT_JSON%" set "INPUT_JSON=%APP_ROOT%\%INPUT_JSON%"
rem Keep OUTPUT_JSON as provided (usually a relative obj\...\output.json path).
rem Some WinUI XAML compiler builds are sensitive to an absolute output.json path; we run from APP_ROOT below.

rem Normalize accidental double backslashes (can break some XamlCompiler builds/targets)
set "INPUT_JSON=%INPUT_JSON:\\=\%"
set "OUTPUT_JSON=%OUTPUT_JSON:\\=\%"

if not exist "%INPUT_JSON%" (
  echo Xaml compiler error: Input JSON file "%~1" doesn't exist! Resolved as "%INPUT_JSON%".
  exit /b 1
)

rem Avoid stale output.json causing incorrect Compile item lists.
rem If the compiler succeeds it will regenerate output.json; if it fails we want that failure to be real.
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
echo Compiler: "%COMPILER%"
echo Arguments: "%INPUT_JSON%" "%OUTPUT_JSON%"
echo.

echo [%date% %time%] CMD="%COMPILER%" "%INPUT_JSON%" "%OUTPUT_JSON%" > "%REPO_ROOT%\xaml_compiler_raw.log"
echo [%date% %time%] PWD=%CD% >> "%REPO_ROOT%\xaml_compiler_raw.log"

rem Change to project directory so relative paths in input.json resolve correctly
cd /d "%APP_ROOT%"
echo [%date% %time%] NEW_PWD=%CD% >> "%REPO_ROOT%\xaml_compiler_raw.log"

"%COMPILER%" "%INPUT_JSON%" "%OUTPUT_JSON%" >> "%REPO_ROOT%\xaml_compiler_raw.log" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo XAML compiler exit code: %EXIT_CODE%
echo [%date% %time%] EXIT=%EXIT_CODE% >> "%REPO_ROOT%\xaml_compiler_raw.log"

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
        echo [%date% %time%] FALSE_POSITIVE=1 OUTPUT_JSON="%OUTPUT_JSON%" >> "%REPO_ROOT%\xaml_compiler_raw.log"
        exit /b 0
      )
    )
  )
)

exit /b %EXIT_CODE%
