@echo off
REM VoiceStudio Ultimate Batch Installer
REM Professional installer for VoiceStudio WinUI application
REM Version: 1.0.0

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo   VoiceStudio Ultimate Installer v1.0.0
echo ===============================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Administrator privileges required!
    echo Please run this installer as Administrator.
    echo.
    pause
    exit /b 1
)

echo Administrator privileges confirmed.
echo.

REM Set installation paths
set "INSTALL_DIR=C:\Program Files\VoiceStudio"
set "DATA_DIR=C:\ProgramData\VoiceStudio"
set "USER_DIR=%USERPROFILE%\VoiceStudio"
set "LOG_FILE=installer.log"

echo Installation paths:
echo   Install Directory: %INSTALL_DIR%
echo   Data Directory: %DATA_DIR%
echo   User Directory: %USER_DIR%
echo   Log File: %LOG_FILE%
echo.

REM Create log file
echo [%date% %time%] Starting VoiceStudio Ultimate installation > %LOG_FILE%

REM Step 1: Check system requirements
echo Step 1: Checking system requirements...
call :CheckSystemRequirements
if %errorlevel% neq 0 (
    echo ERROR: System requirements not met!
    echo Check %LOG_FILE% for details.
    pause
    exit /b 1
)
echo System requirements check passed.
echo.

REM Step 2: Install dependencies
echo Step 2: Installing dependencies...
call :InstallDependencies
if %errorlevel% neq 0 (
    echo ERROR: Dependency installation failed!
    echo Check %LOG_FILE% for details.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

REM Step 3: Create directory structure
echo Step 3: Creating directory structure...
call :CreateDirectories
if %errorlevel% neq 0 (
    echo ERROR: Directory creation failed!
    echo Check %LOG_FILE% for details.
    pause
    exit /b 1
)
echo Directory structure created successfully.
echo.

REM Step 4: Copy application files
echo Step 4: Copying application files...
call :CopyFiles
if %errorlevel% neq 0 (
    echo ERROR: File copying failed!
    echo Check %LOG_FILE% for details.
    pause
    exit /b 1
)
echo Application files copied successfully.
echo.

REM Step 5: Build application
echo Step 5: Building application...
call :BuildApplication
if %errorlevel% neq 0 (
    echo ERROR: Application build failed!
    echo Check %LOG_FILE% for details.
    pause
    exit /b 1
)
echo Application built successfully.
echo.

REM Step 6: Create shortcuts
echo Step 6: Creating shortcuts...
call :CreateShortcuts
if %errorlevel% neq 0 (
    echo WARNING: Shortcut creation failed!
    echo Check %LOG_FILE% for details.
)
echo Shortcuts created successfully.
echo.

REM Step 7: Create Windows service
echo Step 7: Creating Windows service...
call :CreateService
if %errorlevel% neq 0 (
    echo WARNING: Service creation failed!
    echo Check %LOG_FILE% for details.
)
echo Windows service created successfully.
echo.

REM Step 8: Create configuration
echo Step 8: Creating configuration...
call :CreateConfiguration
if %errorlevel% neq 0 (
    echo ERROR: Configuration creation failed!
    echo Check %LOG_FILE% for details.
    pause
    exit /b 1
)
echo Configuration created successfully.
echo.

REM Step 9: Run post-installation tests
echo Step 9: Running post-installation tests...
call :RunTests
if %errorlevel% neq 0 (
    echo WARNING: Some tests failed!
    echo Check %LOG_FILE% for details.
)
echo Post-installation tests completed.
echo.

REM Step 10: Create uninstaller
echo Step 10: Creating uninstaller...
call :CreateUninstaller
if %errorlevel% neq 0 (
    echo WARNING: Uninstaller creation failed!
    echo Check %LOG_FILE% for details.
)
echo Uninstaller created successfully.
echo.

REM Installation completed
echo ===============================================
echo   Installation completed successfully!
echo ===============================================
echo.
echo VoiceStudio Ultimate has been installed to:
echo   %INSTALL_DIR%
echo.
echo You can now start VoiceStudio from:
echo   - Desktop shortcut: VoiceStudio Ultimate
echo   - Start Menu: VoiceStudio ^> VoiceStudio Ultimate
echo   - Command line: %INSTALL_DIR%\bin\VoiceStudioWinUI.exe
echo.
echo For support and documentation, see:
echo   %INSTALL_DIR%\README.md
echo   %INSTALL_DIR%\INSTALLATION_GUIDE.md
echo.
echo Installation log: %LOG_FILE%
echo.

echo [%date% %time%] Installation completed successfully >> %LOG_FILE%

pause
exit /b 0

REM ===============================================
REM Functions
REM ===============================================

:CheckSystemRequirements
echo [%date% %time%] Checking system requirements >> %LOG_FILE%

REM Check Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo Windows version: %VERSION%
if %VERSION% LSS 10.0 (
    echo ERROR: Windows 10 or later required!
    echo [%date% %time%] ERROR: Windows version check failed >> %LOG_FILE%
    exit /b 1
)

REM Check .NET runtime
dotnet --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: .NET runtime not found!
    echo Please install .NET Desktop Runtime 8.0
    echo [%date% %time%] WARNING: .NET runtime not found >> %LOG_FILE%
) else (
    echo .NET runtime found
)

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.11 or later
    echo [%date% %time%] ERROR: Python not found >> %LOG_FILE%
    exit /b 1
) else (
    echo Python found
)

REM Check available memory
for /f "skip=1" %%p in ('wmic computersystem get TotalPhysicalMemory') do (
    if not "%%p"=="" (
        set /a MEMORY_GB=%%p/1024/1024/1024
        echo Available memory: !MEMORY_GB! GB
        if !MEMORY_GB! LSS 4 (
            echo WARNING: Less than 4GB RAM available!
            echo [%date% %time%] WARNING: Insufficient memory >> %LOG_FILE%
        )
        goto :memory_check_done
    )
)
:memory_check_done

REM Check disk space
for /f "tokens=3" %%a in ('dir /-c %INSTALL_DIR%\.. ^| find "bytes free"') do set FREE_SPACE=%%a
set /a FREE_SPACE_GB=%FREE_SPACE%/1024/1024/1024
echo Available disk space: %FREE_SPACE_GB% GB
if %FREE_SPACE_GB% LSS 10 (
    echo ERROR: Less than 10GB disk space available!
    echo [%date% %time%] ERROR: Insufficient disk space >> %LOG_FILE%
    exit /b 1
)

echo [%date% %time%] System requirements check passed >> %LOG_FILE%
exit /b 0

:InstallDependencies
echo [%date% %time%] Installing dependencies >> %LOG_FILE%

REM Install Python packages
echo Installing Python packages...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install fastapi uvicorn numpy torch transformers tokenizers psutil websockets aiohttp >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python packages!
    echo [%date% %time%] ERROR: Python package installation failed >> %LOG_FILE%
    exit /b 1
)

echo [%date% %time%] Dependencies installed successfully >> %LOG_FILE%
exit /b 0

:CreateDirectories
echo [%date% %time%] Creating directory structure >> %LOG_FILE%

REM Create main directories
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\bin" 2>nul
mkdir "%INSTALL_DIR%\services" 2>nul
mkdir "%INSTALL_DIR%\config" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul

REM Create data directories
mkdir "%DATA_DIR%" 2>nul
mkdir "%DATA_DIR%\workers" 2>nul
mkdir "%DATA_DIR%\workers\ops" 2>nul
mkdir "%DATA_DIR%\models" 2>nul
mkdir "%DATA_DIR%\cache" 2>nul

REM Create user directories
mkdir "%USER_DIR%" 2>nul
mkdir "%USER_DIR%\outputs" 2>nul
mkdir "%USER_DIR%\temp" 2>nul

echo [%date% %time%] Directory structure created successfully >> %LOG_FILE%
exit /b 0

:CopyFiles
echo [%date% %time%] Copying application files >> %LOG_FILE%

REM Copy WinUI application
if exist "VoiceStudioWinUI" (
    xcopy "VoiceStudioWinUI" "%INSTALL_DIR%\VoiceStudioWinUI" /E /I /Q >nul
    echo Copied WinUI application
) else (
    echo WARNING: VoiceStudioWinUI directory not found!
)

REM Copy services
if exist "services" (
    xcopy "services" "%INSTALL_DIR%\services" /E /I /Q >nul
    echo Copied services
) else (
    echo WARNING: services directory not found!
)

REM Copy workers
if exist "C:\ProgramData\VoiceStudio\workers" (
    xcopy "C:\ProgramData\VoiceStudio\workers" "%DATA_DIR%\workers" /E /I /Q >nul
    echo Copied workers
) else (
    echo WARNING: workers directory not found!
)

REM Copy solution files
if exist "VoiceStudio.sln" (
    copy "VoiceStudio.sln" "%INSTALL_DIR%\" >nul
    echo Copied solution file
)

if exist "VoiceStudio.Contracts" (
    xcopy "VoiceStudio.Contracts" "%INSTALL_DIR%\VoiceStudio.Contracts" /E /I /Q >nul
    echo Copied contracts project
)

if exist "UltraClone.EngineService" (
    xcopy "UltraClone.EngineService" "%INSTALL_DIR%\UltraClone.EngineService" /E /I /Q >nul
    echo Copied engine service
)

REM Copy configuration files
if exist "config" (
    xcopy "config" "%INSTALL_DIR%\config" /E /I /Q >nul
    echo Copied configuration files
)

echo [%date% %time%] Application files copied successfully >> %LOG_FILE%
exit /b 0

:BuildApplication
echo [%date% %time%] Building application >> %LOG_FILE%

REM Build solution
cd /d "%INSTALL_DIR%"
if exist "VoiceStudio.sln" (
    echo Building solution...
    dotnet build VoiceStudio.sln --configuration Release --verbosity quiet >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Solution build failed!
        echo [%date% %time%] ERROR: Solution build failed >> %LOG_FILE%
        exit /b 1
    )
    echo Solution built successfully
)

REM Publish WinUI application
if exist "VoiceStudioWinUI\VoiceStudioWinUI.csproj" (
    echo Publishing WinUI application...
    dotnet publish VoiceStudioWinUI\VoiceStudioWinUI.csproj --configuration Release --runtime win-x64 --self-contained true --output bin --verbosity quiet >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: WinUI application publish failed!
        echo [%date% %time%] ERROR: WinUI publish failed >> %LOG_FILE%
        exit /b 1
    )
    echo WinUI application published successfully
)

echo [%date% %time%] Application built successfully >> %LOG_FILE%
exit /b 0

:CreateShortcuts
echo [%date% %time%] Creating shortcuts >> %LOG_FILE%

REM Create desktop shortcut
set "DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\VoiceStudio Ultimate.lnk"
set "TARGET_PATH=%INSTALL_DIR%\bin\VoiceStudioWinUI.exe"
set "WORKING_DIR=%INSTALL_DIR%"

REM Create VBScript to create shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%DESKTOP_SHORTCUT%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%TARGET_PATH%" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%WORKING_DIR%" >> CreateShortcut.vbs
echo oLink.Description = "VoiceStudio Ultimate Voice Cloning Application" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript CreateShortcut.vbs >nul 2>&1
del CreateShortcut.vbs >nul 2>&1

echo Desktop shortcut created

REM Create start menu shortcuts
set "START_MENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\VoiceStudio"
mkdir "%START_MENU_DIR%" 2>nul

REM Create main application shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateStartMenuShortcut.vbs
echo sLinkFile = "%START_MENU_DIR%\VoiceStudio Ultimate.lnk" >> CreateStartMenuShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateStartMenuShortcut.vbs
echo oLink.TargetPath = "%TARGET_PATH%" >> CreateStartMenuShortcut.vbs
echo oLink.WorkingDirectory = "%WORKING_DIR%" >> CreateStartMenuShortcut.vbs
echo oLink.Description = "VoiceStudio Ultimate Voice Cloning Application" >> CreateStartMenuShortcut.vbs
echo oLink.Save >> CreateStartMenuShortcut.vbs

cscript CreateStartMenuShortcut.vbs >nul 2>&1
del CreateStartMenuShortcut.vbs >nul 2>&1

echo Start menu shortcuts created

echo [%date% %time%] Shortcuts created successfully >> %LOG_FILE%
exit /b 0

:CreateService
echo [%date% %time%] Creating Windows service >> %LOG_FILE%

REM Create service script
echo import win32serviceutil > "%INSTALL_DIR%\bin\voice_studio_service.py"
echo import win32service >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo import win32event >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo import servicemanager >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo import sys >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo import os >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo import subprocess >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo import time >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo from pathlib import Path >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo. >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo class VoiceStudioService(win32serviceutil.ServiceFramework): >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo     _svc_name_ = "VoiceStudio" >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo     _svc_display_name_ = "VoiceStudio Ultimate Service" >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo     _svc_description_ = "VoiceStudio Ultimate Voice Cloning Service" >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo. >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo     def __init__(self, args): >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         win32serviceutil.ServiceFramework.__init__(self, args) >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None) >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         self.is_running = True >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo. >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo     def SvcStop(self): >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         win32event.SetEvent(self.hWaitStop) >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         self.is_running = False >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo. >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo     def SvcDoRun(self): >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo                             servicemanager.PYS_SERVICE_STARTED, >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo                             (self._svc_name_, '')) >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         self.main() >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo. >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo     def main(self): >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         install_dir = Path("%INSTALL_DIR%") >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         service_script = install_dir / "services" / "voice_cloning" / "ultimate_web_server.py" >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo. >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         if service_script.exists(): >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo             process = subprocess.Popen([ >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo                 sys.executable, str(service_script), "--host", "127.0.0.1", "--port", "8083" >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo             ]) >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo. >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo             while self.is_running: >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo                 time.sleep(1) >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo. >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo             process.terminate() >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo. >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo if __name__ == '__main__': >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo     if len(sys.argv) == 1: >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         servicemanager.Initialize() >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         servicemanager.PrepareToHostSingle(VoiceStudioService) >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         servicemanager.StartServiceCtrlDispatcher() >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo     else: >> "%INSTALL_DIR%\bin\voice_studio_service.py"
echo         win32serviceutil.HandleCommandLine(VoiceStudioService) >> "%INSTALL_DIR%\bin\voice_studio_service.py"

REM Install service
python "%INSTALL_DIR%\bin\voice_studio_service.py" install >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Service installation failed!
    echo [%date% %time%] WARNING: Service installation failed >> %LOG_FILE%
) else (
    echo Windows service created successfully
)

echo [%date% %time%] Windows service creation completed >> %LOG_FILE%
exit /b 0

:CreateConfiguration
echo [%date% %time%] Creating configuration >> %LOG_FILE%

REM Create main configuration
echo { > "%INSTALL_DIR%\config\voice_studio_config.json"
echo   "application": { >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "name": "VoiceStudio Ultimate", >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "version": "1.0.0", >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "install_directory": "%INSTALL_DIR%", >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "data_directory": "%DATA_DIR%", >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "user_directory": "%USER_DIR%" >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo   }, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo   "services": { >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "web_server": { >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "host": "127.0.0.1", >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "port": 8083, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "enabled": true >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     }, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "realtime_service": { >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "enabled": true, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "buffer_size": 100, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "latency_mode": "low" >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     } >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo   }, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo   "ai_models": { >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "gpt_sovits_2": { >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "enabled": true, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "path": "%DATA_DIR%\\models\\gpt_sovits_2" >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     }, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "coqui_xtts_3": { >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "enabled": true, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo       "path": "%DATA_DIR%\\models\\coqui_xtts_3" >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     } >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo   }, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo   "workers": { >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "max_workers": 32, >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "worker_directory": "%DATA_DIR%\\workers", >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo     "enabled": true >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo   } >> "%INSTALL_DIR%\config\voice_studio_config.json"
echo } >> "%INSTALL_DIR%\config\voice_studio_config.json"

echo Configuration created successfully

echo [%date% %time%] Configuration created successfully >> %LOG_FILE%
exit /b 0

:RunTests
echo [%date% %time%] Running post-installation tests >> %LOG_FILE%

REM Test web server
echo Testing web server...
if exist "%INSTALL_DIR%\services\voice_cloning\ultimate_web_server.py" (
    echo Web server script found
) else (
    echo WARNING: Web server script not found!
)

REM Test WinUI application
echo Testing WinUI application...
if exist "%INSTALL_DIR%\bin\VoiceStudioWinUI.exe" (
    echo WinUI application executable found
) else (
    echo WARNING: WinUI application executable not found!
)

REM Test Windows service
echo Testing Windows service...
sc query VoiceStudio >nul 2>&1
if %errorlevel% equ 0 (
    echo VoiceStudio service found
) else (
    echo WARNING: VoiceStudio service not found!
)

echo [%date% %time%] Post-installation tests completed >> %LOG_FILE%
exit /b 0

:CreateUninstaller
echo [%date% %time%] Creating uninstaller >> %LOG_FILE%

REM Create uninstaller script
echo @echo off > "%INSTALL_DIR%\bin\uninstall.bat"
echo REM VoiceStudio Ultimate Uninstaller >> "%INSTALL_DIR%\bin\uninstall.bat"
echo echo Uninstalling VoiceStudio Ultimate... >> "%INSTALL_DIR%\bin\uninstall.bat"
echo. >> "%INSTALL_DIR%\bin\uninstall.bat"
echo REM Stop and remove service >> "%INSTALL_DIR%\bin\uninstall.bat"
echo net stop VoiceStudio ^>nul 2^>^&1 >> "%INSTALL_DIR%\bin\uninstall.bat"
echo sc delete VoiceStudio ^>nul 2^>^&1 >> "%INSTALL_DIR%\bin\uninstall.bat"
echo. >> "%INSTALL_DIR%\bin\uninstall.bat"
echo REM Remove directories >> "%INSTALL_DIR%\bin\uninstall.bat"
echo rmdir /s /q "%INSTALL_DIR%" ^>nul 2^>^&1 >> "%INSTALL_DIR%\bin\uninstall.bat"
echo rmdir /s /q "%DATA_DIR%" ^>nul 2^>^&1 >> "%INSTALL_DIR%\bin\uninstall.bat"
echo rmdir /s /q "%USER_DIR%" ^>nul 2^>^&1 >> "%INSTALL_DIR%\bin\uninstall.bat"
echo. >> "%INSTALL_DIR%\bin\uninstall.bat"
echo REM Remove registry entries >> "%INSTALL_DIR%\bin\uninstall.bat"
echo reg delete "HKLM\SOFTWARE\VoiceStudio" /f ^>nul 2^>^&1 >> "%INSTALL_DIR%\bin\uninstall.bat"
echo reg delete "HKCR\.vsproj" /f ^>nul 2^>^&1 >> "%INSTALL_DIR%\bin\uninstall.bat"
echo reg delete "HKCR\VoiceStudio.Project" /f ^>nul 2^>^&1 >> "%INSTALL_DIR%\bin\uninstall.bat"
echo. >> "%INSTALL_DIR%\bin\uninstall.bat"
echo echo VoiceStudio Ultimate uninstalled successfully! >> "%INSTALL_DIR%\bin\uninstall.bat"
echo pause >> "%INSTALL_DIR%\bin\uninstall.bat"

echo Uninstaller created successfully

echo [%date% %time%] Uninstaller created successfully >> %LOG_FILE%
exit /b 0