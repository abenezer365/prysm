$ErrorActionPreference = "Stop"
$port = 4000
$envFile = Join-Path $PSScriptRoot ".env"

if (Test-Path -LiteralPath $envFile) {
  $setting = Get-Content -LiteralPath $envFile | Where-Object { $_ -match '^PORT=\d+$' } | Select-Object -Last 1
  if ($setting) { $port = [int]($setting -replace '^PORT=', '') }
}

$listeners = netstat.exe -ano -p tcp | Select-String "^\s*TCP\s+\S+:$port\s+\S+\s+LISTENING\s+(\d+)\s*$"
foreach ($listener in $listeners) {
  $ownerPid = [int]$listener.Matches[0].Groups[1].Value
  Write-Host "Stopping stale backend process on port $port (PID $ownerPid)..."
  taskkill.exe /PID $ownerPid /T /F | Out-Null
}

Push-Location $PSScriptRoot
try { & npm.cmd run dev } finally { Pop-Location }
