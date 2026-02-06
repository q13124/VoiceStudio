; VoiceStudio Quantum+ Prerequisite Checks
; Shared prerequisite detection functions for the installer
;
; This file is included by VoiceStudio.iss and provides runtime detection
; for required dependencies: .NET 8 Desktop Runtime, Windows App SDK Runtime.

[Code]

// ============================================================================
// Windows App SDK Runtime Detection
// ============================================================================
// VoiceStudio requires Windows App SDK 1.4+ for WinUI 3 unpackaged deployment.
// The runtime is typically installed at:
//   C:\Program Files\WindowsApps\Microsoft.WindowsAppRuntime.*
// Or registered in:
//   HKLM\SOFTWARE\Microsoft\WindowsAppRuntime

function IsWindowsAppSDKInstalled: Boolean;
var
  RuntimePath: String;
  FindRec: TFindRec;
  SearchPath: String;
  VersionKey: String;
begin
  Result := False;
  
  // Method 1: Check registry for Windows App SDK installation
  // The runtime registers under HKLM\SOFTWARE\Microsoft\WindowsAppRuntime
  if RegKeyExists(HKLM64, 'SOFTWARE\Microsoft\WindowsAppRuntime') then
  begin
    Result := True;
    Exit;
  end;
  
  // Method 2: Check for WindowsAppRuntime packages in WindowsApps folder
  // This covers cases where registry entry might be missing
  SearchPath := ExpandConstant('{commonpf64}\WindowsApps');
  if DirExists(SearchPath) then
  begin
    // Look for Microsoft.WindowsAppRuntime.* directories
    if FindFirst(SearchPath + '\Microsoft.WindowsAppRuntime.*', FindRec) then
    begin
      Result := True;
      FindClose(FindRec);
      Exit;
    end;
  end;
  
  // Method 3: Check for the main runtime DLL in system32
  // Microsoft.WindowsAppRuntime.Bootstrap.dll is the bootstrap DLL
  RuntimePath := ExpandConstant('{sys}\Microsoft.WindowsAppRuntime.Bootstrap.dll');
  if FileExists(RuntimePath) then
  begin
    Result := True;
    Exit;
  end;
end;

function GetWindowsAppSDKDownloadURL: String;
begin
  // Microsoft's official Windows App SDK download page
  Result := 'https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/downloads';
end;

procedure PromptWindowsAppSDKDownload;
var
  ErrorCode: Integer;
begin
  if MsgBox('VoiceStudio Quantum+ requires the Windows App SDK Runtime.'#13#10#13#10 +
            'The runtime was not found on this system.'#13#10#13#10 +
            'Would you like to open the download page?'#13#10#13#10 +
            'After installing the runtime, please run this installer again.',
            mbConfirmation, MB_YESNO) = IDYES then
  begin
    ShellExec('open', GetWindowsAppSDKDownloadURL, '', '', SW_SHOW, ewNoWait, ErrorCode);
  end;
end;

// ============================================================================
// Python Runtime Detection (Optional)
// ============================================================================
// VoiceStudio's backend requires Python 3.10-3.12 for engine execution.
// This is optional at install time but required for full functionality.

function GetPythonVersion: String;
var
  PythonPath: String;
  Version: String;
begin
  Result := '';
  
  // Check Python 3.12
  if RegQueryStringValue(HKLM64, 'SOFTWARE\Python\PythonCore\3.12\InstallPath', '', PythonPath) then
  begin
    Result := '3.12';
    Exit;
  end;
  
  // Check Python 3.11
  if RegQueryStringValue(HKLM64, 'SOFTWARE\Python\PythonCore\3.11\InstallPath', '', PythonPath) then
  begin
    Result := '3.11';
    Exit;
  end;
  
  // Check Python 3.10
  if RegQueryStringValue(HKLM64, 'SOFTWARE\Python\PythonCore\3.10\InstallPath', '', PythonPath) then
  begin
    Result := '3.10';
    Exit;
  end;
  
  // Also check HKCU for per-user Python installations
  if RegQueryStringValue(HKCU, 'SOFTWARE\Python\PythonCore\3.12\InstallPath', '', PythonPath) then
  begin
    Result := '3.12';
    Exit;
  end;
  
  if RegQueryStringValue(HKCU, 'SOFTWARE\Python\PythonCore\3.11\InstallPath', '', PythonPath) then
  begin
    Result := '3.11';
    Exit;
  end;
  
  if RegQueryStringValue(HKCU, 'SOFTWARE\Python\PythonCore\3.10\InstallPath', '', PythonPath) then
  begin
    Result := '3.10';
    Exit;
  end;
end;

function IsPythonInstalled: Boolean;
begin
  Result := GetPythonVersion <> '';
end;

// ============================================================================
// Prerequisite Summary
// ============================================================================
// Call this function to get a summary of all prerequisites for logging

function GetPrerequisiteSummary: String;
var
  Summary: String;
  PythonVer: String;
begin
  Summary := 'Prerequisite Check Summary:'#13#10;
  Summary := Summary + '----------------------------'#13#10;
  
  // .NET 8 Desktop Runtime (checked in main VoiceStudio.iss)
  Summary := Summary + '.NET 8 Desktop Runtime: ';
  if IsDotNet8DesktopInstalled then
    Summary := Summary + 'INSTALLED'#13#10
  else
    Summary := Summary + 'NOT FOUND'#13#10;
  
  // Windows App SDK Runtime
  Summary := Summary + 'Windows App SDK Runtime: ';
  if IsWindowsAppSDKInstalled then
    Summary := Summary + 'INSTALLED'#13#10
  else
    Summary := Summary + 'NOT FOUND'#13#10;
  
  // Python (optional)
  Summary := Summary + 'Python: ';
  PythonVer := GetPythonVersion;
  if PythonVer <> '' then
    Summary := Summary + 'INSTALLED (v' + PythonVer + ')'#13#10
  else
    Summary := Summary + 'NOT FOUND (optional)'#13#10;
  
  Result := Summary;
end;

