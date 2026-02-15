"""
Update PanelRegistry.Auto.cs with all discovered panels
"""

from pathlib import Path


def discover_all_panels(workspace_root):
    """Discover all panel XAML files."""
    workspace = Path(workspace_root)
    all_panels = set()

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
        "app/ui/VoiceStudio.App/Views",
        "Views/Panels",
        "Views",
        "Panels"
    ]

    print("Searching for panels...")
    print()

    for dir_name in search_dirs:
        full_path = workspace / dir_name
        if full_path.exists():
            print(f"  Searching: {dir_name}")
            for pattern in patterns:
                for panel_file in full_path.rglob(pattern):
                    # Get relative path
                    rel_path = panel_file.relative_to(workspace)
                    rel_str = str(rel_path).replace("\\", "/")
                    if rel_str not in all_panels:
                        all_panels.add(rel_str)
                        print(f"    Found: {rel_str}")

    # Also search for ViewModels
    print()
    print("Searching for ViewModels...")
    for dir_name in search_dirs:
        full_path = workspace / dir_name
        if full_path.exists():
            for vm_file in full_path.rglob("*ViewModel.cs"):
                # Try to find corresponding XAML
                xaml_file = vm_file.with_suffix(".xaml")
                if xaml_file.exists():
                    rel_path = xaml_file.relative_to(workspace)
                    rel_str = str(rel_path).replace("\\", "/")
                    if rel_str not in all_panels:
                        all_panels.add(rel_str)
                        print(f"    Found via ViewModel: {rel_str}")

    # Also search root and all subdirectories for any XAML
    print()
    print("Searching all XAML files...")
    for xaml_file in workspace.rglob("*.xaml"):
        # Skip if already found
        rel_path = xaml_file.relative_to(workspace)
        rel_str = str(rel_path).replace("\\", "/")

        # Only include if it looks like a panel/view
        if (rel_str not in all_panels and
            ("View" in xaml_file.name or "Panel" in xaml_file.name or
             "View" in rel_str or "Panel" in rel_str)):
            all_panels.add(rel_str)
            print(f"    Found: {rel_str}")

    sorted_panels = sorted(all_panels)

    print()
    print("=" * 60)
    print(f"Found {len(sorted_panels)} panels")
    print("=" * 60)
    print()

    return sorted_panels

def generate_registry(panels, output_file):
    """Generate PanelRegistry.Auto.cs"""
    panel_list = "\n".join([f'      "{panel}",' for panel in panels])

    code = f"""using System.Collections.Generic;

namespace VoiceStudio.Core {{

  public static class PanelRegistryAuto {{

    public static IEnumerable<string> AllXaml() => new [] {{
{panel_list}
    }};

  }}

}}
"""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(code, encoding='utf-8')
    print(f"Generated: {output_file}")
    print(f"  Contains {len(panels)} panels")

if __name__ == "__main__":
    workspace = Path("E:/VoiceStudio")
    output_file = workspace / "app" / "core" / "PanelRegistry.Auto.cs"

    panels = discover_all_panels(workspace)

    if panels:
        generate_registry(panels, output_file)

        # Also create text list
        text_file = output_file.with_suffix(".txt")
        text_file.write_text("\n".join(panels), encoding='utf-8')
        print(f"Panel list saved to: {text_file}")
        print()
        print("Discovery complete!")
    else:
        print("No panels found!")

