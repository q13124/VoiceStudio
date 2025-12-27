import json
import sys

input_json_path = r"e:\VoiceStudio\src\VoiceStudio.App\obj\Debug\net8.0-windows10.0.19041.0\input.json"

try:
    with open(input_json_path, "r", encoding="utf-8") as f:
        d = json.load(f)

    print("=== input.json Key Details ===")
    print(f"\nLocalAssembly: {d.get('LocalAssembly', 'NOT_SET')}")
    print(f"IsPass1: {d.get('IsPass1', 'NOT_SET')}")
    print(f"ProjectName: {d.get('ProjectName', 'NOT_SET')}")
    print(f"TargetFileName: {d.get('TargetFileName', 'NOT_SET')}")

    refs = d.get("ReferenceAssemblies", [])
    print(f"\nReferenceAssemblies count: {len(refs)}")
    print("Sample ReferenceAssemblies (first 5):")
    for i, r in enumerate(refs[:5]):
        item_spec = r.get("ItemSpec", "?")
        full_path = r.get("FullPath", "?")
        print(f"  [{i+1}] ItemSpec: {item_spec}")
        print(f"      FullPath: {full_path}")

    # Check for AppXManifest
    appx_manifest = d.get("AppXManifest", "NOT_SET")
    print(f"\nAppXManifest: {appx_manifest}")

    # Show all keys for reference
    print(f"\nAll keys in input.json: {sorted(d.keys())}")

except FileNotFoundError:
    print(f"ERROR: {input_json_path} not found. Run Pass1 first.")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
