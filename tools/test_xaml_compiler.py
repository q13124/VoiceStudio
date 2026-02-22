"""
XAML compiler diagnostic script - invokes XamlCompiler.exe with input.json.
Moved to tools/ per Arch Review Task 1.3.
Run from repo root. Adjust paths for your environment.
"""
import json
import os
import subprocess

# Paths - adjust for your environment
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
obj_dir = os.path.join(
    repo_root,
    "src",
    "VoiceStudio.App",
    "obj",
    "x64",
    "Debug",
    "net8.0-windows10.0.19041.0",
)
proj_dir = os.path.join(repo_root, "src", "VoiceStudio.App")
compiler = os.path.expandvars(
    r"%USERPROFILE%\.nuget\packages\microsoft.windowsappsdk.winui\1.8.251105000\tools\net472\XamlCompiler.exe"
)

input_path = os.path.join(obj_dir, "input.json")
if not os.path.exists(input_path):
    print(f"ERROR: {input_path} not found. Run a build first.")
    exit(1)

d = json.load(open(input_path))

# Print key properties
for k in [
    "CompileMode",
    "IsPass1",
    "OutputPath",
    "OutputType",
    "ProjectPath",
    "SavedStateFile",
    "XamlPlatform",
    "DisableXbfGeneration",
    "XAMLFingerprint",
    "ProjectName",
    "PriIndexName",
]:
    print(f"{k}: {d.get(k, 'NOT SET')}")

# Keep all pages - test from project directory
bisect_path = os.path.join(obj_dir, "bisect_input.json")
bisect_output = os.path.join(obj_dir, "bisect_output.json")

# Use full pages list
json.dump(d, open(bisect_path, "w"))
print(f"\nPages: {len(d['XamlPages'])}")

if os.path.exists(bisect_output):
    os.remove(bisect_output)

# Run from PROJECT directory
result = subprocess.run(
    [compiler, bisect_path, bisect_output],
    capture_output=True,
    text=True,
    timeout=60,
    cwd=proj_dir,
)
print(f"Exit code: {result.returncode}")
print(f"stdout: {result.stdout[:500]}")
print(f"stderr: {result.stderr[:500]}")
print(f"Output exists: {os.path.exists(bisect_output)}")
