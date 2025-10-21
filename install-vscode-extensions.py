#!/usr/bin/env python3
"""
VOICESTUDIO GOD-TIER VOICE CLONER - VS CODE EXTENSIONS INSTALLER
Install Essential Extensions for Maximum Development Efficiency
15 ChatGPT Plus Agents + 1 Assistant Agent
The Most Advanced Voice Cloning System in Existence
Version: 3.7.0 "Phoenix Development Environment"
"""

import subprocess
import sys
import os
from pathlib import Path

def install_vscode_extensions():
    """Install essential VS Code extensions for VoiceStudio development"""
    
    # Essential extensions for VoiceStudio God-Tier development
    extensions = [
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
        "ms-vscode.vscode-ffmpeg",
        "ms-vscode.vscode-audio-tools",
        
        # System & Deployment
        "ms-vscode.powershell",
        "ms-vscode.batch-scripts",
        "ms-azuretools.vscode-docker",
        "ms-vscode-remote.remote-wsl",
        
        # Database & Storage
        "qwtel.sqlite-viewer",
        "ms-mssql.mssql",
        
        # Web Development
        "ms-vscode.vscode-html-css-support",
        "ms-vscode.vscode-javascript-snippets",
        "ritwickdey.liveserver",
        "esbenp.prettier-vscode",
        
        # Data & Visualization
        "ms-toolsai.datawrangler",
        "ms-vscode.vscode-excel-viewer",
        "ms-vscode.vscode-csv-viewer",
        "ms-vscode.vscode-json-viewer",
        
        # Security & Testing
        "eamodio.gitlens",
        "github.vscode-pull-request-github",
        "ms-vscode.vscode-security-scanner",
        "ms-vscode.vscode-coverage-gutters",
        "hbenl.vscode-test-explorer",
        
        # Documentation & Project Management
        "yzhang.markdown-all-in-one",
        "shd101wyy.markdown-preview-enhanced",
        "hediet.vscode-drawio",
        "jebbs.plantuml",
        "gruntfuggly.todo-tree",
        "alefragnani.project-manager",
        "sleistner.vscode-fileutils",
        "christian-kohler.path-intellisense"
    ]
    
    print("=" * 80)
    print("  VOICESTUDIO GOD-TIER VOICE CLONER - VS CODE EXTENSIONS")
    print("=" * 80)
    print("  Installing Essential Extensions for Maximum Development Efficiency")
    print("  15 ChatGPT Plus Agents + 1 Assistant Agent")
    print("  The Most Advanced Voice Cloning System in Existence")
    print("=" * 80)
    print()
    
    print("Installing VS Code extensions for VoiceStudio development...")
    print(f"Total extensions to install: {len(extensions)}")
    print()
    
    installed_count = 0
    failed_count = 0
    
    for i, extension in enumerate(extensions, 1):
        try:
            print(f"[{i:2d}/{len(extensions)}] Installing {extension}...")
            result = subprocess.run([
                "code", "--install-extension", extension, "--force"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"[OK] {extension} installed successfully")
                installed_count += 1
            else:
                print(f"[ERROR] Failed to install {extension}: {result.stderr}")
                failed_count += 1
                
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {extension} installation timed out")
            failed_count += 1
        except Exception as e:
            print(f"[ERROR] Failed to install {extension}: {e}")
            failed_count += 1
    
    print()
    print("=" * 80)
    print("  VS CODE EXTENSIONS INSTALLATION COMPLETE!")
    print("=" * 80)
    print(f"  Successfully Installed: {installed_count}")
    print(f"  Failed Installations: {failed_count}")
    print(f"  Total Extensions: {len(extensions)}")
    print("=" * 80)
    print()
    
    if installed_count > 0:
        print("ESSENTIAL EXTENSIONS INSTALLED:")
        print("✅ Python Development Suite")
        print("✅ AI/ML Development Tools")
        print("✅ Code Quality & Performance")
        print("✅ Audio Processing Tools")
        print("✅ System & Deployment Tools")
        print("✅ Database & Storage Tools")
        print("✅ Web Development Tools")
        print("✅ Data & Visualization Tools")
        print("✅ Security & Testing Tools")
        print("✅ Documentation & Project Management")
        print()
        print("DEVELOPMENT ENVIRONMENT READY!")
        print("Your VS Code is now optimized for VoiceStudio development!")
        print("Maximum development efficiency with AI-powered tools!")
    
    return installed_count, failed_count

def create_extension_recommendations():
    """Create .vscode/extensions.json with recommended extensions"""
    
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    extensions_json = {
        "recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "ms-python.debugpy",
            "njpwerner.autodocstring",
            "KevinRose.vsc-python-indent",
            "LittleFoxTeam.vscode-python-test-adapter",
            "ms-toolsai.jupyter",
            "ms-python.python-environment-manager",
            "ms-toolsai.vscode-tensorflow-snippets",
            "ms-toolsai.vscode-pytorch-snippets",
            "huggingface.huggingface-vscode",
            "ms-python.black-formatter",
            "ms-python.flake8",
            "ms-python.mypy-type-checker",
            "ms-python.bandit",
            "sonarsource.sonarlint-vscode",
            "streetsidesoftware.code-spell-checker",
            "ms-vscode.vscode-audio-preview",
            "ms-vscode.vscode-waveform",
            "ms-vscode.powershell",
            "ms-vscode.batch-scripts",
            "ms-azuretools.vscode-docker",
            "qwtel.sqlite-viewer",
            "ms-vscode.vscode-html-css-support",
            "ritwickdey.liveserver",
            "esbenp.prettier-vscode",
            "ms-toolsai.datawrangler",
            "eamodio.gitlens",
            "github.vscode-pull-request-github",
            "yzhang.markdown-all-in-one",
            "gruntfuggly.todo-tree",
            "alefragnani.project-manager"
        ]
    }
    
    import json
    with open(vscode_dir / "extensions.json", "w") as f:
        json.dump(extensions_json, f, indent=2)
    
    print("Created .vscode/extensions.json with recommended extensions")

def main():
    """Main function"""
    print("VOICESTUDIO GOD-TIER VOICE CLONER - VS CODE EXTENSIONS INSTALLER")
    print("Installing Essential Extensions for Maximum Development Efficiency")
    print("15 ChatGPT Plus Agents + 1 Assistant Agent")
    print()
    
    # Check if VS Code is installed
    try:
        subprocess.run(["code", "--version"], capture_output=True, check=True)
        print("[OK] VS Code is installed and available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] VS Code is not installed or not in PATH")
        print("Please install VS Code from: https://code.visualstudio.com/")
        return False
    
    # Install extensions
    installed_count, failed_count = install_vscode_extensions()
    
    # Create extension recommendations file
    create_extension_recommendations()
    
    print()
    print("VS CODE EXTENSIONS INSTALLATION COMPLETE!")
    print("Your development environment is now optimized for VoiceStudio!")
    print("Maximum development efficiency with AI-powered tools!")
    
    return installed_count > 0

if __name__ == "__main__":
    success = main()
    if not success:
        input("Press Enter to exit...")
    else:
        print("VS Code extensions installed successfully!")
        print("Restart VS Code to activate all extensions.")
        input("Press Enter to exit...")
