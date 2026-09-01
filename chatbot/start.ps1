$ErrorActionPreference = "Stop"
$python = Join-Path (Split-Path -Parent $PSScriptRoot) ".venv\Scripts\python.exe"
$port = 8200
$envFile = Join-Path $PSScriptRoot ".env"

if (-not (Test-Path -LiteralPath $python)) {
  throw "Prysm virtual environment not found at $python"
}

if (Test-Path -LiteralPath $envFile) {
  $portSetting = Get-Content -LiteralPath $envFile | Where-Object { $_ -match '^RAG_PORT=\d+$' } | Select-Object -Last 1
  if ($portSetting) { $port = [int]($portSetting -replace '^RAG_PORT=', '') }
}

$listeners = netstat.exe -ano -p tcp | Select-String "^\s*TCP\s+\S+:$port\s+\S+\s+LISTENING\s+(\d+)\s*$"
foreach ($listener in $listeners) {
  $ownerPid = [int]$listener.Matches[0].Groups[1].Value
  Write-Host "Stopping stale chatbot process on port $port (PID $ownerPid)..."
  taskkill.exe /PID $ownerPid /T /F | Out-Null
}

& $python (Join-Path $PSScriptRoot "main.py")
