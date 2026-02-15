"""
Panel Verification Script
Verifies all panels are discovered and registered
"""

import re
import sys
from pathlib import Path


def find_all_panels(workspace_root):
    """Find all panel XAML files."""
    workspace = Path(workspace_root)

    # Search patterns
    patterns = ["*View.xaml", "*Panel.xaml"]

    # Search directories
    search_dirs = [
        "ui/Views/Panels",
        "ui/Views",
        "ui/Panels",
        "src/VoiceStudio.App/Views/Panels",
        "src/VoiceStudio.App/Views",
        "src/VoiceStudio.App/Panels",
        "app/ui/panels",
        "app/ui/views",
        "Views/Panels",
        "Views",
        "Panels"
    ]

    panels = set()

    for dir_path in search_dirs:
        full_path = workspace / dir_path
        if full_path.exists():
            for pattern in patterns:
                for panel_file in full_path.rglob(pattern):
                    # Get relative path
                    rel_path = panel_file.relative_to(workspace)
                    panels.add(str(rel_path).replace("\\", "/"))

    # Also check ViewModels
    for dir_path in search_dirs:
        full_path = workspace / dir_path
        if full_path.exists():
            for vm_file in full_path.rglob("*ViewModel.cs"):
                # Try to find corresponding XAML
                xaml_file = vm_file.with_suffix(".xaml")
                if xaml_file.exists():
                    rel_path = xaml_file.relative_to(workspace)
                    panels.add(str(rel_path).replace("\\", "/"))

    return sorted(panels)

def check_panel_registry(workspace_root):
    """Check PanelRegistry.Auto.cs."""
    workspace = Path(workspace_root)
    registry_file = workspace / "app" / "core" / "PanelRegistry.Auto.cs"

    if not registry_file.exists():
        print("  [ERROR] PanelRegistry.Auto.cs not found")
        return []

    # Extract panel paths from registry
    content = registry_file.read_text(encoding='utf-8')
    # Find all quoted strings
    pattern = r'"([^"]+\.xaml)"'
    registered = re.findall(pattern, content)

    return registered

def main():
    """Run panel verification."""
    workspace_root = Path(__file__).parent.parent.parent

    print("=" * 60)
    print("Panel Verification")
    print("=" * 60)
    print()

    # Find all panels
    print("[1] Discovering panels in workspace...")
    all_panels = find_all_panels(workspace_root)
    print(f"  Found {len(all_panels)} panels")
    print()

    # Check registry
    print("[2] Checking PanelRegistry.Auto.cs...")
    registered = check_panel_registry(workspace_root)
    print(f"  Registered: {len(registered)} panels")
    print()

    # Compare
    print("[3] Comparing...")
    all_set = set(all_panels)
    registered_set = set(registered)

    missing = all_set - registered_set
    extra = registered_set - all_set

    if missing:
        print(f"  [WARNING] Missing from registry ({len(missing)} panels):")
        for panel in sorted(missing)[:10]:
            print(f"    - {panel}")
        if len(missing) > 10:
            print(f"    ... and {len(missing) - 10} more")
    else:
        print("  [OK] All discovered panels are registered")

    if extra:
        print(f"  [WARNING] Extra in registry ({len(extra)} panels):")
        for panel in sorted(extra)[:10]:
            print(f"    - {panel}")
        if len(extra) > 10:
            print(f"    ... and {len(extra) - 10} more")

    print()

    # Summary
    print("=" * 60)
    if not missing and not extra:
        print("[SUCCESS] All panels properly registered!")
        return 0
    else:
        print("[ISSUES FOUND]:")
        if missing:
            print(f"  - {len(missing)} panels missing from registry")
        if extra:
            print(f"  - {len(extra)} panels in registry but not found")
        print()
        print("Run: .\tools\\Find-AllPanels.ps1 to regenerate PanelRegistry.Auto.cs")
        return 1

if __name__ == "__main__":
    sys.exit(main())

