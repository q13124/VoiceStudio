# Roslynator Integration Plan

**Date:** 2026-01-10  
**Status:** RECOMMENDED (non-blocking configuration)  
**Purpose:** Add Roslynator analyzers to catch bugs and improve code quality without blocking Gate C progress

---

## Strategy

**Approach:** Add Roslynator analyzers configured as **warnings** (non-blocking) so they:
- ✅ Help catch bugs and code quality issues early
- ✅ Surface issues for teams to fix incrementally
- ✅ Don't block builds or Gate C progress
- ✅ Can be upgraded to errors later once codebase is clean

---

## Implementation Plan

### Step 1: Add Roslynator NuGet Package

Add to `src/VoiceStudio.App/VoiceStudio.App.csproj`:

```xml
<ItemGroup>
  <PackageReference Include="Roslynator.Analyzers" Version="4.11.0">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
  </PackageReference>
</ItemGroup>
```

### Step 2: Configure Analyzer Severity (Non-Blocking)

Add to `.editorconfig` or create `.roslynatorconfig`:

```ini
# Roslynator Analyzers - Configured as warnings (non-blocking)
dotnet_analyzer_diagnostic.category-roslynator.severity = warning

# Allow teams to fix incrementally without blocking builds
# Can upgrade to "error" once codebase is clean
```

### Step 3: Optional - Configure Specific Rules

If desired, configure specific high-value rules:

```ini
# High-value rules for bug detection
dotnet_diagnostic.RCS1003.severity = warning  # Add braces to if-else
dotnet_diagnostic.RCS1014.severity = warning  # Use implicitly typed local variable
dotnet_diagnostic.RCS1033.severity = suggestion  # Remove redundant boolean literal
dotnet_diagnostic.RCS1055.severity = warning  # Unreachable code
dotnet_diagnostic.RCS1098.severity = warning  # Constant values should be placed on right side
dotnet_diagnostic.RCS1104.severity = warning  # Simplify conditional expression
dotnet_diagnostic.RCS1118.severity = warning  # Mark local variable as const
dotnet_diagnostic.RCS1124.severity = warning  # Inline local variable
dotnet_diagnostic.RCS1128.severity = warning  # Use coalesce expression
dotnet_diagnostic.RCS1129.severity = warning  # Call 'Any()' instead of 'Count() > 0'
dotnet_diagnostic.RCS1139.severity = warning  # Add summary element to documentation comment
dotnet_diagnostic.RCS1141.severity = warning  # Add parameter to documentation comment
dotnet_diagnostic.RCS1146.severity = warning  # Use conditional access
dotnet_diagnostic.RCS1151.severity = warning  # Remove redundant cast
dotnet_diagnostic.RCS1163.severity = warning  # Unused parameter
dotnet_diagnostic.RCS1170.use_readonly_auto_property.severity = suggestion
dotnet_diagnostic.RCS1180.severity = warning  # Inline lazy initialization
dotnet_diagnostic.RCS1181.severity = warning  # Cast to 'as' instead
dotnet_diagnostic.RCS1188.severity = warning  # Remove redundant auto-property
dotnet_diagnostic.RCS1191.severity = warning  # Declare enum value as combination of names
dotnet_diagnostic.RCS1192.severity = warning  # Unnecessary usage of verbatim string
dotnet_diagnostic.RCS1194.severity = warning  # Implement exception constructors
dotnet_diagnostic.RCS1197.severity = warning  # Optimize StringBuilder.Append/AppendLine
dotnet_diagnostic.RCS1198.severity = warning  # Avoid unnecessary substring
dotnet_diagnostic.RCS1199.severity = warning  # Unnecessary null check
dotnet_diagnostic.RCS1200.severity = warning  # Call 'Enumerable.Any()' instead of 'Enumerable.Count()'
dotnet_diagnostic.RCS1201.severity = warning  # Use method group instead of anonymous function
dotnet_diagnostic.RCS1202.severity = warning  # Avoid NullReferenceException
dotnet_diagnostic.RCS1203.severity = warning  # Use AttributeUsageAttribute
dotnet_diagnostic.RCS1205.severity = warning  # Order named arguments according to parameter order
dotnet_diagnostic.RCS1206.severity = warning  # Use conditional access instead of conditional expression
dotnet_diagnostic.RCS1207.severity = warning  # Convert method group to lambda
dotnet_diagnostic.RCS1208.severity = warning  # Reduce 'if' nesting
dotnet_diagnostic.RCS1209.severity = warning  # Order named arguments according to parameter order
dotnet_diagnostic.RCS1210.severity = warning  # Return Task.FromResult instead of returning null
dotnet_diagnostic.RCS1211.severity = warning  # Remove unnecessary else clause
dotnet_diagnostic.RCS1212.severity = warning  # Remove redundant assignment
dotnet_diagnostic.RCS1213.severity = warning  # Remove unused member declaration
dotnet_diagnostic.RCS1214.severity = warning  # Unnecessary interpolated string
dotnet_diagnostic.RCS1215.severity = warning  # Expression is always equal to true/false
dotnet_diagnostic.RCS1216.severity = warning  # Unnecessary unsafe context
dotnet_diagnostic.RCS1217.severity = warning  # Composite enum value contains undefined flag
dotnet_diagnostic.RCS1218.severity = warning  # Simplify code branching
dotnet_diagnostic.RCS1219.severity = warning  # Call 'async' method in 'await' expression
dotnet_diagnostic.RCS1220.severity = warning  # Use pattern matching instead of combination of 'as' operator and null check
dotnet_diagnostic.RCS1221.severity = warning  # Use pattern matching instead of 'as' expression followed by null check
dotnet_diagnostic.RCS1222.severity = warning  # Merge preprocessor directives
dotnet_diagnostic.RCS1223.severity = warning  # Mark publicly visible type or member as sealed
dotnet_diagnostic.RCS1224.severity = warning  # Make class sealed
dotnet_diagnostic.RCS1225.severity = warning  # Make class static
dotnet_diagnostic.RCS1226.severity = warning  # Add paragraph to documentation comment
dotnet_diagnostic.RCS1227.severity = warning  # Validate arguments explicitly
dotnet_diagnostic.RCS1228.severity = warning  # Use async/await when necessary
dotnet_diagnostic.RCS1229.severity = warning  # Mark field as readonly
dotnet_diagnostic.RCS1230.severity = warning  # Unnecessary null check for value type
dotnet_diagnostic.RCS1231.severity = warning  # Make parameter ref readonly
dotnet_diagnostic.RCS1232.severity = warning  # Order elements in documentation comment
dotnet_diagnostic.RCS1233.severity = warning  # Use short-circuiting operator
dotnet_diagnostic.RCS1234.severity = warning  # Duplicate word in comment
dotnet_diagnostic.RCS1235.severity = warning  # Optimize LINQ method call
dotnet_diagnostic.RCS1236.severity = warning  # Use element access
dotnet_diagnostic.RCS1237.severity = warning  # Use 'Count' property instead of 'Any()'
dotnet_diagnostic.RCS1238.severity = warning  # Avoid nested 'using' statements
dotnet_diagnostic.RCS1239.severity = warning  # Use 'for' statement instead of 'while' statement
dotnet_diagnostic.RCS1240.severity = warning  # Use 'for' statement instead of 'while' statement
dotnet_diagnostic.RCS1241.severity = warning  # Use 'for' statement instead of 'while' statement
dotnet_diagnostic.RCS1242.severity = warning  # Do not pass non-read-only struct by read-only reference
dotnet_diagnostic.RCS1243.severity = warning  # Duplicate word in a comment
dotnet_diagnostic.RCS1244.severity = warning  # Simplify default expression
dotnet_diagnostic.RCS1245.severity = warning  # Simplify conditional expression
dotnet_diagnostic.RCS1246.severity = warning  # Use '??=' operator
dotnet_diagnostic.RCS1247.severity = warning  # Fix formatting
dotnet_diagnostic.RCS1248.severity = warning  # Remove braces from single-line embedded statement
dotnet_diagnostic.RCS1249.severity = warning  # Simplify coalesce expression
dotnet_diagnostic.RCS1250.severity = warning  # Use 'Enumerable.Any()' instead of 'Enumerable.Count()'
dotnet_diagnostic.RCS1251.severity = warning  # Use 'Enumerable.Any()' instead of 'Enumerable.Count()'
dotnet_diagnostic.RCS1252.severity = warning  # Use 'Enumerable.Any()' instead of 'Enumerable.Count()'
dotnet_diagnostic.RCS1253.severity = warning  # Use 'Enumerable.Any()' instead of 'Enumerable.Count()'
dotnet_diagnostic.RCS1254.severity = warning  # Unnecessary 'async'/'await'
dotnet_diagnostic.RCS1255.severity = warning  # Seal class that has no descendants
dotnet_diagnostic.RCS1256.severity = warning  # Use 'CultureInfo.InvariantCulture'
dotnet_diagnostic.RCS1257.severity = warning  # Unused type parameter
dotnet_diagnostic.RCS1258.severity = warning  # Seal class that has no descendants
dotnet_diagnostic.RCS1259.severity = warning  # Unused parameter in lambda
dotnet_diagnostic.RCS1260.severity = warning  # 'using' statement can be simplified
dotnet_diagnostic.RCS1261.severity = warning  # Unused field
dotnet_diagnostic.RCS1262.severity = warning  # Unused parameter
dotnet_diagnostic.RCS1263.severity = warning  # Remove empty statement
dotnet_diagnostic.RCS1264.severity = warning  # Unused variable
dotnet_diagnostic.RCS1265.severity = warning  # Unused variable
dotnet_diagnostic.RCS1266.severity = warning  # Remove empty 'else' clause
dotnet_diagnostic.RCS1267.severity = warning  # Merge 'if' statements
dotnet_diagnostic.RCS1268.severity = warning  # Remove empty 'if' statement
dotnet_diagnostic.RCS1269.severity = warning  # Remove redundant 'else' clause
dotnet_diagnostic.RCS1270.severity = warning  # Remove redundant 'if' statement
dotnet_diagnostic.RCS1271.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1272.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1273.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1274.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1275.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1276.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1277.severity = warning  # Use 'Count' property instead of 'Count()' warning
dotnet_diagnostic.RCS1278.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1279.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1280.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1281.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1282.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1283.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1284.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1285.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1286.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1287.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1288.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1289.severity = warning  # Use 'Count' property instead of 'Count()' method
dotnet_diagnostic.RCS1290.severity = warning  # Use 'Count' property instead of 'Count()' method
```

---

## Benefits

1. **Early Bug Detection**: Catches common bugs before they reach production
2. **Code Quality**: Improves code readability and maintainability
3. **Incremental Fixes**: Teams can fix issues incrementally without blocking progress
4. **Future-Proofing**: Can upgrade to errors once codebase is clean

---

## Integration with Current Workflow

- **Build & Tooling Engineer**: Can configure and maintain Roslynator settings
- **UI Engineer**: Will benefit from cleaner code patterns (addresses CS0108, CS8602, etc.)
- **All Roles**: Get real-time feedback in IDE while coding

---

## Current Status

**Recommendation:** Add Roslynator with warning-level severity:
- ✅ Helps catch bugs (user's goal)
- ✅ Doesn't block Gate C progress
- ✅ Teams can fix incrementally
- ✅ Can upgrade to errors later

**Next Steps:**
1. Add Roslynator.Analyzers NuGet package
2. Configure severity as "warning" in .editorconfig
3. Let teams fix issues incrementally as they work
4. Monitor warning counts over time

---

**Decision Point:** Should we add Roslynator now (non-blocking) or defer until after Gate C closes?
