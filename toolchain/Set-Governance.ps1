param(
  [ValidateSet("on","off")]
  [string]$State = "off"
)
$ErrorActionPreference='Stop'
if(-not (Test-Path "STATE")){ New-Item -Type Directory STATE | Out-Null }
$flag = "STATE\governance.off"
if($State -eq "off"){
  "off" | Out-File $flag -Force
  $env:ULTRACLONE_GOVERNANCE="off"
  Write-Host "Governing AI/Cursor governance: OFF" -ForegroundColor Yellow
}else{
  if(Test-Path $flag){ Remove-Item $flag -Force }
  $env:ULTRACLONE_GOVERNANCE="on"
  Write-Host "Governing AI/Cursor governance: ON" -ForegroundColor Green
}
