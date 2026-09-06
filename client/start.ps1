$ErrorActionPreference = "Stop"
$port = 5173

$listeners = netstat.exe -ano -p tcp | Select-String "^\s*TCP\s+\S+:$port\s+\S+\s+LISTENING\s+(\d+)\s*$"
foreach ($listener in $listeners) {
  $ownerPid = [int]$listener.Matches[0].Groups[1].Value
  Write-Host "Stopping stale frontend process on port $port (PID $ownerPid)..."
  taskkill.exe /PID $ownerPid /T /F | Out-Null
}

Push-Location $PSScriptRoot
try { & npm.cmd start } finally { Pop-Location }
