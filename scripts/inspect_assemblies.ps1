$paths = @(
  'C:\Program Files\dotnet\shared\Microsoft.WindowsDesktop.App\6.0.36\System.Security.Permissions.dll',
  'C:\Users\Tyler\.nuget\packages\microsoft.windowsappsdk\1.5.240627000\tools\net6.0\Microsoft.UI.Xaml.Markup.Compiler.dll'
)
foreach ($path in $paths) {
  if (Test-Path $path) {
    try {
      $an = [System.Reflection.AssemblyName]::GetAssemblyName($path)
      $pt = $an.GetPublicKeyToken()
      $hex = ($pt | ForEach-Object { $_.ToString('x2') }) -join ''
      Write-Output "Path: $path"
      Write-Output "  Name: $($an.Name)"
      Write-Output "  Version: $($an.Version)"
      Write-Output "  PublicKeyToken: $hex"
      Write-Output ""
    }
    catch {
      Write-Output (("Failed to read assembly info for {0}: {1}") -f $path, $_.Exception.Message)
    }
  }
  else {
    Write-Output "Not found: $path"
  }
}
