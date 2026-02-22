"""
Run React/Electron panel discovery and show results
"""

import subprocess
import sys
from pathlib import Path


def main():
    script_path = Path("E:/VoiceStudio/tools/Discover-ReactPanels.ps1")

    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        return 1

    print("=" * 60)
    print("Running React/Electron Panel Discovery")
    print("=" * 60)
    print()

    try:
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script_path),
                "-SourcePath",
                "C:\\VoiceStudio",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("STDERR:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)

        print()
        print("=" * 60)
        print(f"Discovery completed (exit code: {result.returncode})")
        print("=" * 60)

        # Check for catalog files
        catalog_json = Path("E:/VoiceStudio/docs/governance/REACT_PANEL_CATALOG.json")
        catalog_md = Path("E:/VoiceStudio/docs/governance/REACT_PANEL_CATALOG.md")

        if catalog_json.exists():
            print()
            print("✓ Catalog generated!")
            print(f"  JSON: {catalog_json}")

            import json

            with open(catalog_json, encoding="utf-8") as f:
                data = json.load(f)
                print(f"  Total panels: {data.get('totalPanels', 0)}")
                print(f"  Electron detected: {data.get('electron', {}).get('hasElectron', False)}")

        if catalog_md.exists():
            print(f"  Markdown: {catalog_md}")

        return result.returncode

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
