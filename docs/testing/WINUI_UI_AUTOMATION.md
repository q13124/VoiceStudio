# WinUI UI Automation (TASK-004)

Purpose: provide a repeatable WinUI automation harness for smoke-level UI checks using WinAppDriver/Appium.

## Prerequisites

- Windows 10/11 with Desktop App Installer.
- WinAppDriver (1.2) running locally:
  - Download: https://github.com/microsoft/WinAppDriver/releases/tag/v1.2.1
  - Launch: `WinAppDriver.exe 127.0.0.1 4723`
- Built app executable (Release recommended):
  - `dotnet build "E:\VoiceStudio\VoiceStudio.sln" -c Release -p:Platform=x64`
  - App path: `E:\VoiceStudio\.buildlogs\x64\Release\net8.0-windows10.0.19041.0\win-x64\VoiceStudio.App.exe`

## Environment variables

- `VS_APP_PATH`: full path to `VoiceStudio.App.exe` (Release or Debug build)
- `WINAPPDRIVER_URL` (optional): defaults to `http://127.0.0.1:4723`

## Running the UI smoke test

```powershell
# From repo root
dotnet test src/VoiceStudio.App.UITests/VoiceStudio.App.UITests.csproj -c Release -p:Platform=x64
```

Notes:
- Tests are `Inconclusive` when `VS_APP_PATH` is not set to avoid false negatives.
- Ensure WinAppDriver is running **before** executing tests.

## Why WinAppDriver/Appium

- Works with unpackaged WinUI 3 apps.
- Simple capabilities (`app` = path to exe) allow direct attach without MSIX packaging.
- Extensible for richer flows (element location, input simulation) as the suite grows.
