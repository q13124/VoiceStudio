; VoiceStudio Inno Setup Script
; Phase 7: Installer Script
; Task 7.5: Inno Setup installer configuration

#define MyAppName "VoiceStudio"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "VoiceStudio"
#define MyAppURL "https://voicestudio.app"
#define MyAppExeName "VoiceStudio.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{8F7C9A2E-5D3B-4C1A-9E6F-0D8A7B6C5E4D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/support
AppUpdatesURL={#MyAppURL}/updates
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\..\..\LICENSE.txt
OutputDir=..\..\..\dist\installer
OutputBaseFilename=VoiceStudio-{#MyAppVersion}-Setup
SetupIconFile=..\..\..\assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0.19041

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Components]
Name: "main"; Description: "Core Application"; Types: full compact custom; Flags: fixed
Name: "engines"; Description: "Voice Synthesis Engines"; Types: full
Name: "models"; Description: "Pre-trained Voice Models"; Types: full
Name: "samples"; Description: "Sample Projects"; Types: full
Name: "docs"; Description: "Documentation"; Types: full compact

[Files]
; Main application
Source: "..\..\..\dist\VoiceStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: main

; Engines
Source: "..\..\..\dist\engines\*"; DestDir: "{app}\engines"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: engines

; Models
Source: "..\..\..\dist\models\*"; DestDir: "{app}\models"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: models

; Samples
Source: "..\..\..\samples\*"; DestDir: "{app}\samples"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: samples

; Documentation
Source: "..\..\..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: docs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; File associations
Root: HKCR; Subkey: ".vsproj"; ValueType: string; ValueName: ""; ValueData: "VoiceStudio.Project"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "VoiceStudio.Project"; ValueType: string; ValueName: ""; ValueData: "VoiceStudio Project"; Flags: uninsdeletekey
Root: HKCR; Subkey: "VoiceStudio.Project\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCR; Subkey: "VoiceStudio.Project\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

Root: HKCR; Subkey: ".vsarc"; ValueType: string; ValueName: ""; ValueData: "VoiceStudio.Archive"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "VoiceStudio.Archive"; ValueType: string; ValueName: ""; ValueData: "VoiceStudio Archive"; Flags: uninsdeletekey
Root: HKCR; Subkey: "VoiceStudio.Archive\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},1"
Root: HKCR; Subkey: "VoiceStudio.Archive\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

; App paths
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\VoiceStudio.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DownloadPage: TDownloadWizardPage;

// Check for .NET Runtime
function IsDotNetInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('dotnet', '--list-runtimes', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

// Check for Visual C++ Redistributable
function IsVCRedistInstalled(): Boolean;
begin
  Result := RegKeyExists(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\X64');
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check Windows version
  if not IsWin64 then
  begin
    MsgBox('VoiceStudio requires a 64-bit version of Windows.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = wpReady then
  begin
    // Check prerequisites
    if not IsDotNetInstalled() then
    begin
      if MsgBox('.NET Runtime is not installed. Would you like to download it?', mbConfirmation, MB_YESNO) = IDYES then
      begin
        ShellExec('open', 'https://dotnet.microsoft.com/download/dotnet/8.0', '', '', SW_SHOWNORMAL, ewNoWait, ResultCode);
      end;
      Result := False;
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Ask to remove user data
    if MsgBox('Would you like to remove all user data (projects, settings, voices)?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{localappdata}\VoiceStudio'), True, True, True);
      DelTree(ExpandConstant('{userappdata}\VoiceStudio'), True, True, True);
    end;
  end;
end;
