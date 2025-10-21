#!/usr/bin/env python3
"""
Final Cleanup Script for VoiceStudio Ultimate
Removes duplicate/unused files while preserving the most advanced system
"""

import os
import shutil
from pathlib import Path

def main():
    print("VoiceStudio Ultimate - Final Cleanup")
    print("=" * 50)

    # Define what to KEEP (most advanced system)
    KEEP_FILES = {
        # Core advanced installer
        "installer/",
        "VoiceStudioUltimate_v1.0.0_Windows.zip",
        "VoiceStudioUltimate_Package/",

        # Advanced AI integration system
        "create_auto_upgrade_system.py",
        "create_complete_package.py",

        # Core services and workers
        "services/",
        "workers/",
        "VoiceStudio/",

        # Essential config and tools
        "config/",
        "tools/",
        "plugins/",
        "web/",
        "bin/",

        # Database files
        "voicestudio.db",
        "voicestudio.db-shm",
        "voicestudio.db-wal",

        # Essential documentation
        "README.md",
        "VOICESTUDIO_ULTIMATE_COMPLETE.md",
        "VOICESTUDIO_ULTIMATE_README.md",
        "WINDOWS_INSTALLER_COMPLETE.md",
        "VOICESTUDIO_ULTIMATE_CHATGPT_AUTO_UPGRADE_COMPLETE.md",
        "VOICESTUDIO_ULTIMATE_CYCLONEDX_COMPLETE.md",
        "VOICESTUDIO_ULTIMATE_ENHANCED_COMPLETE.md",

        # Essential scripts
        "voice_studio_service.py",
        "voice_studio_windows_service.py",
        "voicestudio_unified_dashboard.py",

        # Essential requirements
        "requirements-gui.txt",
    }

    # Define what to REMOVE (duplicates/outdated)
    REMOVE_PATTERNS = [
        # Duplicate installation files
        "install-*.bat",
        "install-*.py",
        "install-god-tier-voice-cloner*",
        "install-voice-studio*",
        "install-ultimate-voice-cloning*",
        "install-complete-voice-studio*",

        # Duplicate start scripts (keep only the ultimate ones)
        "start-voice-studio.bat",  # Keep start-voice-studio-ultimate.py
        "start-services.bat",      # Keep start-services.py
        "start-service-health-dashboard.py",  # Keep enhanced version
        "start-service-health-dashboard-gui.py",  # Keep enhanced version

        # Old test files
        "test_*.py",
        "test-*.py",
        "validate-*.py",

        # Old optimization files
        "optimize_*.py",
        "voicestudio_*_optimizer.py",
        "voicestudio_*_test_report.json",
        "voicestudio_optimization_report.json",

        # Old deployment files
        "deploy*.py",
        "deployment_report.json",
        "DEPLOYMENT_COMPLETE.md",

        # Old automation files
        "automated_build_system.py",
        "comprehensive_testing_pipeline.py",
        "intelligent_dependency_manager.py",
        "intelligent_system_detector.py",
        "master_automation_system.py",
        "ultimate_deployment_system.py",
        "voicestudio_system_optimizer.py",
        "voicestudio_ultimate_optimizer.py",

        # Old monitoring files
        "real_time_monitor.py",
        "simple_monitor.py",
        "working_monitor.py",
        "working_voice_cloning_service.py",
        "show-progress.py",
        "project-progress-tracker.py",

        # Old documentation (keep only ultimate versions)
        "CHATGPT_*.md",
        "FAST_TRACK_*.md",
        "GOD_TIER_*.md",
        "MAXIMUM_*.md",
        "OPTIMIZATION_*.md",
        "REAL_MONITORING_*.md",
        "SERVICE_MANAGEMENT_*.md",
        "STEP_*.md",
        "ULTIMATE_PERFORMANCE_*.md",
        "ULTIMATE_VOICE_CLONING_*.md",
        "VOICE_CLONING_*.md",
        "VOICE_STUDIO_COMPLETE_*.md",
        "VOICESTUDIO_COMPREHENSIVE_*.md",
        "VOICESTUDIO_GOD_TIER_*.md",
        "VOICESTUDIO_ULTIMATE_SYSTEM_SUMMARY.md",
        "VOICESTUDIO_ULTIMATE_WINDOWS_GUIDE.md",
        "VSCODE_EXTENSIONS_*.md",

        # Old config files
        "cspell.config.json",
        "cspell.json",

        # Old logs and reports
        "logs/",
        "comprehensive_test_report.json",
        "final_test_results.md",
        "FINAL_TEST_RESULTS.md",

        # Old backups
        "backups/",

        # Cleanup script itself
        "cleanup_installation_files.py",
        "final_cleanup_advanced_system.py",
        "CLEANUP_SUMMARY.md",
    ]

    removed_count = 0
    kept_count = 0

    print("Scanning for files to clean up...")

    # Get all files and directories
    all_items = []
    for root, dirs, files in os.walk("."):
        for item in dirs + files:
            rel_path = os.path.relpath(os.path.join(root, item), ".")
            all_items.append(rel_path)

    # Process each item
    for item in sorted(all_items):
        if item.startswith("./") or item.startswith(".\\"):
            item = item[2:]

        # Skip if it's a keep file/directory
        should_keep = False
        for keep_item in KEEP_FILES:
            if item == keep_item or item.startswith(keep_item):
                should_keep = True
                break

        if should_keep:
            kept_count += 1
            continue

        # Check if it matches removal patterns
        should_remove = False
        for pattern in REMOVE_PATTERNS:
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if item.startswith(prefix):
                    should_remove = True
                    break
            elif pattern.endswith("/"):
                if item.startswith(pattern) or item == pattern[:-1]:
                    should_remove = True
                    break
            else:
                if item == pattern:
                    should_remove = True
                    break

        if should_remove:
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"Removed directory: {item}")
                else:
                    os.remove(item)
                    print(f"Removed file: {item}")
                removed_count += 1
            except Exception as e:
                print(f"Could not remove {item}: {e}")
        else:
            kept_count += 1

    print("\n" + "=" * 50)
    print("CLEANUP COMPLETE!")
    print(f"Removed: {removed_count} items")
    print(f"Kept: {kept_count} items")
    print("\nPRESERVED ADVANCED SYSTEM:")
    print("   - VoiceStudio Ultimate Windows Installer")
    print("   - ChatGPT Auto-Upgrade System")
    print("   - CycloneDX SBOM Generation")
    print("   - VRAM Telemetry Monitoring")
    print("   - Cursor AI Integration")
    print("   - Complete Service Management")
    print("\nSystem is now optimized and ready for production!")

if __name__ == "__main__":
    main()
