$file = 'E:/VoiceStudio/src/VoiceStudio.Core/Services/Generated/BackendClient.generated.cs'
$backup = $file + '.bak'
if (-not (Test-Path $file)) { Write-Error "File not found: $file"; exit 1 }
Copy-Item -Path $file -Destination $backup -Force
$text = Get-Content -Path $file -Raw -Encoding UTF8
$pattern = '(?m)^(\s*public\s+virtual\s+[^\(\n]+\s+)([A-Za-z_]\w*)(\s*\()'
$matches = [regex]::Matches($text, $pattern)
$nameCounts = @{}
# Collect occurrences in order
$occurrences = @()
foreach ($m in $matches) {
  $start = $m.Index
  $name = $m.Groups[2].Value
  $occurrences += [PSCustomObject]@{Index = $start; Name = $name }
}
# Process from end to start so replacements don't shift indexes of earlier matches
$occurrences = $occurrences | Sort-Object -Property Index -Descending
foreach ($occ in $occurrences) {
  $name = $occ.Name
  if (-not $nameCounts.ContainsKey($name)) { $nameCounts[$name] = 0 }
  $nameCounts[$name] += 1
  $count = $nameCounts[$name]
  if ($count -gt 1) {
    # create new name with suffix
    $newName = "$name`_$count"
    # replace only the specific occurrence at this index
    # find the slice around the index to perform targeted replace
    $sliceStart = [math]::Max(0, $occ.Index - 100)
    $sliceLength = [math]::Min(400, $text.Length - $sliceStart)
    $slice = $text.Substring($sliceStart, $sliceLength)
    $slicePattern = [regex]::Escape($name) + '(\s*\()'
    $newSlice = [regex]::Replace($slice, $slicePattern, "$newName$1", 1)
    # apply back
    $text = $text.Substring(0, $sliceStart) + $newSlice + $text.Substring($sliceStart + $sliceLength)
  }
}
# Write back
Set-Content -Path $file -Value $text -Encoding UTF8
Write-Output "Updated file and backed up original to $backup"
