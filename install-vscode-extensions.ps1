# VOICESTUDIO GOD-TIER VOICE CLONER - VS CODE EXTENSIONS INSTALLER
# PowerShell script to install essential VS Code extensions
# Maximum Development Efficiency with AI-Powered Tools

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  VOICESTUDIO GOD-TIER VOICE CLONER - VS CODE EXTENSIONS INSTALLER" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Installing Essential Extensions for Maximum Development Efficiency" -ForegroundColor Cyan
Write-Host "  15 ChatGPT Plus Agents + 1 Assistant Agent" -ForegroundColor Cyan
Write-Host "  The Most Advanced Voice Cloning System in Existence" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if VS Code is installed
try {
    $codeVersion = & code --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] VS Code is installed and available" -ForegroundColor Green
        Write-Host "Version: $($codeVersion[0])" -ForegroundColor Green
    }
    else {
        throw "VS Code not found"
    }
}
catch {
    Write-Host "[ERROR] VS Code is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install VS Code from: https://code.visualstudio.com/" -ForegroundColor Yellow
    Write-Host "After installation, restart your terminal and run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing VS Code extensions for VoiceStudio development..." -ForegroundColor Yellow
Write-Host ""

# Essential extensions for VoiceStudio God-Tier development
$extensions = @(
    # Core Python Development
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.debugpy",
    "njpwerner.autodocstring",
    "KevinRose.vsc-python-indent",
    "LittleFoxTeam.vscode-python-test-adapter",

    # AI/ML Development
    "ms-toolsai.jupyter",
    "ms-python.python-environment-manager",
    "ms-toolsai.vscode-tensorflow-snippets",
    "ms-toolsai.vscode-pytorch-snippets",
    "huggingface.huggingface-vscode",

    # Code Quality & Performance
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "ms-python.bandit",
    "sonarsource.sonarlint-vscode",
    "streetsidesoftware.code-spell-checker",

    # Audio Processing
    "ms-vscode.vscode-audio-preview",
    "ms-vscode.vscode-waveform",
    "ms-vscode.powershell",
    "ms-vscode.batch-scripts",

    # System & Deployment
    "ms-azuretools.vscode-docker",
    "qwtel.sqlite-viewer",
    "ms-vscode.vscode-html-css-support",
    "ritwickdey.liveserver",
    "esbenp.prettier-vscode",

    # Data & Visualization
    "ms-toolsai.datawrangler",
    "eamodio.gitlens",
    "github.vscode-pull-request-github",
    "yzhang.markdown-all-in-one",
    "gruntfuggly.todo-tree",
    "alefragnani.project-manager",
    "christian-kohler.path-intellisense",
    "ms-vscode.vscode-fileutils",
    "hediet.vscode-drawio",
    "jebbs.plantuml",
    "ms-vscode.vscode-excel-viewer",
    "ms-vscode.vscode-csv-viewer",
    "ms-vscode.vscode-json-viewer",
    "hbenl.vscode-test-explorer",
    "ms-vscode.vscode-coverage-gutters",
    "ms-vscode.vscode-security-scanner"
)

$installedCount = 0
$failedCount = 0
$totalExtensions = $extensions.Count

Write-Host "Total extensions to install: $totalExtensions" -ForegroundColor Cyan
Write-Host ""

for ($i = 0; $i -lt $extensions.Count; $i++) {
    $extension = $extensions[$i]
    $progress = $i + 1

    try {
        Write-Host "[$progress/$totalExtensions] Installing $extension..." -ForegroundColor Yellow

        $result = & code --install-extension $extension --force 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] $extension installed successfully" -ForegroundColor Green
            $installedCount++
        }
        else {
            Write-Host "[ERROR] Failed to install $extension" -ForegroundColor Red
            $failedCount++
        }

    }
    catch {
        Write-Host "[ERROR] Failed to install $extension : $($_.Exception.Message)" -ForegroundColor Red
        $failedCount++
    }

    # Small delay to prevent overwhelming the extension marketplace
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  VS CODE EXTENSIONS INSTALLATION COMPLETE!" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Successfully Installed: $installedCount" -ForegroundColor Green
Write-Host "  Failed Installations: $failedCount" -ForegroundColor Red
Write-Host "  Total Extensions: $totalExtensions" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

if ($installedCount -gt 0) {
    Write-Host "ESSENTIAL EXTENSIONS INSTALLED:" -ForegroundColor Green
    Write-Host "✅ Python Development Suite" -ForegroundColor Green
    Write-Host "✅ AI/ML Development Tools" -ForegroundColor Green
    Write-Host "✅ Code Quality & Performance" -ForegroundColor Green
    Write-Host "✅ Audio Processing Tools" -ForegroundColor Green
    Write-Host "✅ System & Deployment Tools" -ForegroundColor Green
    Write-Host "✅ Database & Storage Tools" -ForegroundColor Green
    Write-Host "✅ Web Development Tools" -ForegroundColor Green
    Write-Host "✅ Data & Visualization Tools" -ForegroundColor Green
    Write-Host "✅ Security & Testing Tools" -ForegroundColor Green
    Write-Host "✅ Documentation & Project Management" -ForegroundColor Green
    Write-Host ""
    Write-Host "DEVELOPMENT ENVIRONMENT READY!" -ForegroundColor Cyan
    Write-Host "Your VS Code is now optimized for VoiceStudio development!" -ForegroundColor Cyan
    Write-Host "Maximum development efficiency with AI-powered tools!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Restart VS Code to activate all extensions" -ForegroundColor White
    Write-Host "2. Open the VoiceStudio project folder" -ForegroundColor White
    Write-Host "3. VS Code will prompt to install recommended extensions" -ForegroundColor White
    Write-Host "4. Click 'Install All' if prompted" -ForegroundColor White
    Write-Host "5. Use F5 to debug any component" -ForegroundColor White
    Write-Host "6. Use Ctrl+Shift+P → 'Tasks: Run Task' for build tasks" -ForegroundColor White
}
else {
    Write-Host "No extensions were installed successfully." -ForegroundColor Red
    Write-Host "Please check your internet connection and VS Code installation." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "VOICESTUDIO GOD-TIER VOICE CLONER - MAXIMUM DEVELOPMENT EFFICIENCY!" -ForegroundColor Cyan
Write-Host "🚀🎤✨🤖⚡" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
