r"""
Discover panels from C:\VoiceStudio and generate PanelRegistry.Auto.cs
"""

import os
import sys
from pathlib import Path


def discover_panels(source_root="C:\\VoiceStudio", target_root="E:\\VoiceStudio"):
    """Discover all panels from source and generate registry."""

    print("=" * 60)
    print("Panel Discovery from C:\\VoiceStudio")
    print("=" * 60)
    print()

    if not os.path.exists(source_root):
        print(f"ERROR: Source not found: {source_root}")
        return []

    print(f"Source: {source_root}")
    print(f"Target: {target_root}")
    print()

    # Search patterns
    patterns = ["*View.xaml", "*Panel.xaml"]

    # Search directories - comprehensive list
    search_dirs = [
        "ui/Views/Panels",
        "ui/Views",
        "ui/Panels",
        "src",
        "app/ui",
        "Views",
        "Panels",
        "",  # Root directory - search everything
        "app",
        "app/Views",
        "app/Views/Panels",
        "app/ui/panels",
        "app/ui/views",
        "src/VoiceStudio.App",
        "src/VoiceStudio.App/Views",
        "src/VoiceStudio.App/Views/Panels"
    ]

    all_panels = set()

    print("Searching for panels...")
    print()

    for dir_name in search_dirs:
        full_path = Path(source_root) / dir_name
        if full_path.exists():
            print(f"  Searching: {dir_name}")
            for pattern in patterns:
                for panel_file in full_path.rglob(pattern):
                    # Get relative path from source
                    rel_path = panel_file.relative_to(Path(source_root))
                    rel_str = str(rel_path).replace("\\", "/")
                    if rel_str not in all_panels:
                        all_panels.add(rel_str)
                        print(f"    Found: {rel_str}")

    # Also search for ViewModels
    print()
    print("Searching for ViewModels...")
    for dir_name in search_dirs:
        full_path = Path(source_root) / dir_name
        if full_path.exists():
            for vm_file in full_path.rglob("*ViewModel.cs"):
                # Try to find corresponding XAML
                xaml_file = vm_file.with_suffix(".xaml")
                if xaml_file.exists():
                    rel_path = xaml_file.relative_to(Path(source_root))
                    rel_str = str(rel_path).replace("\\", "/")
                    if rel_str not in all_panels:
                        all_panels.add(rel_str)
                        print(f"    Found via ViewModel: {rel_str}")

    sorted_panels = sorted(all_panels)

    print()
    print("=" * 60)
    print(f"Found {len(sorted_panels)} panels")
    print("=" * 60)
    print()

    # Generate PanelRegistry.Auto.cs
    if sorted_panels:
        output_file = Path(target_root) / "app" / "core" / "PanelRegistry.Auto.cs"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        panel_list = "\n".join([f'      "{panel}",' for panel in sorted_panels])

        code = f"""using System.Collections.Generic;

namespace VoiceStudio.Core {{

  public static class PanelRegistryAuto {{

    public static IEnumerable<string> AllXaml() => new [] {{
{panel_list}
    }};

  }}

}}
"""

        output_file.write_text(code, encoding='utf-8')
        print(f"Generated: {output_file}")
        print(f"  Contains {len(sorted_panels)} panels")

        # Also create text list
        text_file = output_file.with_suffix(".txt")
        text_file.write_text("\n".join(sorted_panels), encoding='utf-8')
        print(f"Panel list saved to: {text_file}")

    return sorted_panels

if __name__ == "__main__":
    panels = discover_panels()
    if panels:
        print()
        print("Discovery complete!")
        sys.exit(0)
    else:
        print()
        print("No panels found!")
        sys.exit(1)

