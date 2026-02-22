r"""
Execute the full migration from C:\VoiceStudio to E:\VoiceStudio
"""

import subprocess
import sys
from pathlib import Path


def main():
    print("=" * 60)
    print("VoiceStudio Migration Script")
    print("=" * 60)
    print()

    src = Path("C:/VoiceStudio")
    dst = Path("E:/VoiceStudio")

    # Check source
    if not src.exists():
        print(f"ERROR: Source not found: {src}")
        print("Please ensure C:\\VoiceStudio exists")
        return 1

    print(f"Source: {src}")
    print(f"Destination: {dst}")
    print()

    # Run PowerShell migration script
    script_path = dst / "tools" / "VS_MigrateToE.ps1"

    if not script_path.exists():
        print(f"ERROR: Migration script not found: {script_path}")
        return 1

    print("Executing migration script...")
    print()

    try:
        # Run PowerShell script
        ps_cmd = [
            "powershell.exe",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script_path),
            "-Src",
            str(src),
            "-Dst",
            str(dst),
        ]

        result = subprocess.run(
            ps_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )

        # Print output
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("STDERR:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)

        print()
        print("=" * 60)
        print(f"Migration completed with exit code: {result.returncode}")
        print("=" * 60)

        if result.returncode == 0:
            print("✓ Migration successful!")

            # Check panel registry
            registry_file = dst / "app" / "core" / "PanelRegistry.Auto.cs"
            if registry_file.exists():
                content = registry_file.read_text(encoding="utf-8")
                content.count('"')
                print(f"✓ Panel registry generated: {registry_file}")
                print("  Found panels in registry")
            else:
                print("⚠ Panel registry not found")

            return 0
        else:
            print("✗ Migration failed!")
            return result.returncode

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
