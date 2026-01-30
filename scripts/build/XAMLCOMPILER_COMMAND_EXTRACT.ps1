# Extract XamlCompiler.exe command line from binlog
$binlogPath = "e:\VoiceStudio\artifacts\msbuild_xaml_pass2.binlog"

if (Test-Path $binlogPath) {
    Write-Host "=== XamlCompiler.exe Command Line from binlog ==="
    Write-Host "Binlog: $binlogPath"
    Write-Host ""
    Write-Host "To view: Open in MSBuild Structured Log Viewer"
    Write-Host "Or extract with: dotnet msbuild /bl:$binlogPath /t:MarkupCompilePass2 /v:diag"
    Write-Host ""
    Write-Host "Looking for XamlCompiler command in build output..."
    
    # Try to extract from recent build
    $buildOutput = dotnet build "e:\VoiceStudio\src\VoiceStudio.App\VoiceStudio.App.csproj" -t:MarkupCompilePass2 -v:diag 2>&1
    $xcLine = $buildOutput | Select-String -Pattern "XamlCompiler.exe.*input.json.*output.json" | Select-Object -First 1
    if ($xcLine) {
        Write-Host "Found command line:"
        Write-Host $xcLine.Line
    }
    else {
        Write-Host "Command line not found in output. Check binlog file."
    }
}
else {
    Write-Host "Binlog not found. Run: dotnet build ... -bl:$binlogPath"
}
