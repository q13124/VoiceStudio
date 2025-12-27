; VoiceStudio Quantum+ Inno Setup Installer Script
; Professional Voice Cloning Studio Installer

#define MyAppName "VoiceStudio Quantum+"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "VoiceStudio"
#define MyAppURL "https://voicestudio.example"
#define MyAppExeName "VoiceStudioApp.exe"
#define MyAppId "A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D"

[Setup]
; Basic Information
AppId={#MyAppId}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\VoiceStudio
DefaultGroupName=VoiceStudio
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=Output
OutputBaseFilename=VoiceStudio-Setup-v{#MyAppVersion}
SetupIconFile=..\src\VoiceStudio.App\Assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
MinVersion=10.0.18362

; Uninstall
UninstallDisplayIcon={app}\App\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Frontend Application
Source: "..\src\VoiceStudio.App\bin\Release\net8.0-windows10.0.19041.0\*"; DestDir: "{app}\App"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\src\VoiceStudio.Core\bin\Release\net8.0\*"; DestDir: "{app}\App"; Flags: ignoreversion recursesubdirs createallsubdirs

; Backend Files
Source: "..\backend\api\*.py"; DestDir: "{app}\Backend\api"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\backend\api\routes\*.py"; DestDir: "{app}\Backend\api\routes"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\backend\api\ws\*.py"; DestDir: "{app}\Backend\api\ws"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\backend\requirements.txt"; DestDir: "{app}\Backend"; Flags: ignoreversion

; Core Engine Files
Source: "..\app\core\engines\*.py"; DestDir: "{app}\Core\engines"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\app\core\audio\*.py"; DestDir: "{app}\Core\audio"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\app\core\runtime\*.py"; DestDir: "{app}\Core\runtime"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\app\core\training\*.py"; DestDir: "{app}\Core\training"; Flags: ignoreversion recursesubdirs createallsubdirs

; Engine Manifests
Source: "..\engines\audio\*\engine.manifest.json"; DestDir: "{app}\Engines\audio"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\engines\image\*\engine.manifest.json"; DestDir: "{app}\Engines\image"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\engines\video\*\engine.manifest.json"; DestDir: "{app}\Engines\video"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "..\docs\user\*.md"; DestDir: "{app}\Docs\user"; Flags: ignoreversion
Source: "..\docs\api\*.md"; DestDir: "{app}\Docs\api"; Flags: ignoreversion
Source: "..\docs\developer\*.md"; DestDir: "{app}\Docs\developer"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\App\{#MyAppExeName}"
Name: "{group}\User Manual"; Filename: "{app}\Docs\user\USER_MANUAL.md"
Name: "{group}\Getting Started"; Filename: "{app}\Docs\user\GETTING_STARTED.md"
Name: "{group}\API Documentation"; Filename: "{app}\Docs\api\API_REFERENCE.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\App\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\App\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; File Associations
Root: HKCR; Subkey: ".voiceproj"; ValueType: string; ValueName: ""; ValueData: "VoiceStudio.Project"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "VoiceStudio.Project"; ValueType: string; ValueName: ""; ValueData: "VoiceStudio Project File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "VoiceStudio.Project\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\App\{#MyAppExeName},0"
Root: HKCR; Subkey: "VoiceStudio.Project\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\App\{#MyAppExeName}"" ""%1"""

Root: HKCR; Subkey: ".vprofile"; ValueType: string; ValueName: ""; ValueData: "VoiceStudio.Profile"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "VoiceStudio.Profile"; ValueType: string; ValueName: ""; ValueData: "VoiceStudio Voice Profile"; Flags: uninsdeletekey
Root: HKCR; Subkey: "VoiceStudio.Profile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\App\{#MyAppExeName},1"
Root: HKCR; Subkey: "VoiceStudio.Profile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\App\{#MyAppExeName}"" ""%1"""

; Application Registry
Root: HKLM; Subkey: "SOFTWARE\VoiceStudio"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\VoiceStudio"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey

[Run]
; Check for .NET 8 Runtime
Filename: "{dotnet80runtime}"; StatusMsg: "Checking for .NET 8 Runtime..."; Check: not IsDotNetInstalled

; Install Python Packages (if Python is installed)
Filename: "python"; Parameters: "-m pip install -r ""{app}\Backend\requirements.txt"""; StatusMsg: "Installing Python packages..."; Check: IsPythonInstalled; Flags: runhidden

; Create User Data Directories
Filename: "powershell"; Parameters: "-Command ""New-Item -ItemType Directory -Force -Path $env:APPDATA\VoiceStudio"""; StatusMsg: "Creating user data directories..."; Flags: runhidden

[Code]
function IsDotNetInstalled: Boolean;
var
  Release: Cardinal;
begin
  Result := RegQueryDWordValue(HKLM, 'SOFTWARE\dotnet\Setup\InstalledVersions\x64\sharedhost', 'Version', Release);
  if Result then
    Result := Release >= $08000000; // .NET 8.0
end;

function IsPythonInstalled: Boolean;
var
  PythonPath: String;
begin
  Result := RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\3.10\InstallPath', 'ExecutablePath', PythonPath);
  if not Result then
    Result := RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\3.11\InstallPath', 'ExecutablePath', PythonPath);
  if not Result then
    Result := RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\3.12\InstallPath', 'ExecutablePath', PythonPath);
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check Windows version
  if not IsWin64 then
  begin
    MsgBox('VoiceStudio Quantum+ requires 64-bit Windows.', mbError, MB_OK);
    Result := False;
  end;
  
  // Check .NET 8 Runtime
  if not IsDotNetInstalled then
  begin
    if MsgBox('.NET 8.0 Runtime is required. Would you like to download it now?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://dotnet.microsoft.com/download/dotnet/8.0', '', '', SW_SHOWNORMAL, ewNoWait, Result);
    end;
    Result := False;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  Result := True;
  
  // Optional: Ask user if they want to keep user data
  if MsgBox('Do you want to keep your user data (settings, projects, profiles)?', mbConfirmation, MB_YESNO) = IDNO then
  begin
    // Delete user data
    DelTree(ExpandConstant('{userappdata}\VoiceStudio'), True, True, True);
  end;
end;

