# Pass2 Dependency Ordering Fix

**Date:** 2025-12-22  
**Issue:** MarkupCompilePass2 fails because LocalAssembly is None (assembly doesn't exist yet)  
**Fix:** Added CoreCompile to MarkupCompilePass2DependsOn

---

## Root Cause

Pass2 was running **before** CoreCompile, which meant:
- The compiled assembly didn't exist yet
- `XamlIntermediateAssembly` didn't exist
- `LocalAssembly` remained `None`
- XamlCompiler.exe failed silently (exit code 1, no error details)

---

## Solution Applied

Updated `Directory.Build.targets` to force CoreCompile to run before Pass2:

```xml
<PropertyGroup Condition="'$(MSBuildProjectName)' == 'VoiceStudio.App'">
  <MarkupCompilePass1DependsOn>ResolveReferences;$(MarkupCompilePass1DependsOn)</MarkupCompilePass1DependsOn>
  <!-- Force CoreCompile to run before Pass2 so LocalAssembly exists for validation -->
  <MarkupCompilePass2DependsOn>CoreCompile;$(MarkupCompilePass2DependsOn)</MarkupCompilePass2DependsOn>
</PropertyGroup>
```

---

## Verification

From diagnostic build output:
```
MarkupCompilePass2DependsOn = CoreCompile;
Building target "CoreCompile" completely.
Done building target "CoreCompile" in project "VoiceStudio.App.csproj"
```

✅ **Confirmed:** CoreCompile now runs before Pass2

---

## Expected Behavior

When CoreCompile succeeds:
1. Assembly is compiled and placed in output directory
2. `XamlIntermediateAssembly` item exists (defined in targets file line 208-209)
3. `LocalAssembly` property gets populated (targets file line 644-646 checks `Exists(@(XamlIntermediateAssembly))`)
4. Pass2 receives valid `LocalAssembly` in input.json
5. XamlCompiler.exe can complete Pass2 validation successfully

---

## Current Status

- ✅ Dependency ordering fix implemented
- ✅ CoreCompile confirmed to run before Pass2
- ⚠️ CoreCompile currently fails due to C# compilation errors (separate issue, not related to XAML)

**Next Step:** Once C# compilation errors are resolved, Pass2 should succeed because LocalAssembly will be properly populated.

---

## Technical Details

### Targets File Location
`C:\Users\Tyler\.nuget\packages\microsoft.windowsappsdk.winui\1.8.251105000\buildTransitive\Microsoft.UI.Xaml.Markup.Compiler.interop.targets`

### Key Code Sections

**XamlIntermediateAssembly definition (line 208-209):**
```xml
<XamlIntermediateAssembly Condition="'$(ManagedAssembly)'!='false'" 
    Include="$(XamlGeneratedOutputPath)intermediatexaml\$(TargetName)$(TargetExt)"/>
```

**LocalAssembly population (line 644-646):**
```xml
<LocalAssembly Condition="'$(LocalAssembly)' == '' and Exists(@(XamlIntermediateAssembly))">
    @(XamlIntermediateAssembly->'%(Identity)')
</LocalAssembly>
```

**MarkupCompilePass2 target (line 633-635):**
```xml
<Target Name="MarkupCompilePass2"
        DependsOnTargets="$(MarkupCompilePass2DependsOn)"
        Condition="'@(Page)' != '' Or '@(ApplicationDefinition)' != '' " >
```

---

## References

- Original analysis: `PASS2_DIAGNOSTIC_DATA.md`
- XAML compilation summary: `XAML_COMPILATION_ISSUE_SUMMARY.md`
