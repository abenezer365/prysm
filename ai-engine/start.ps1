$ErrorActionPreference = "Stop"
$python = Join-Path (Split-Path -Parent $PSScriptRoot) ".venv\Scripts\python.exe"
$serverEnv = Join-Path (Split-Path -Parent $PSScriptRoot) "server\.env"
$port = if ($env:AI_PORT) { [int]$env:AI_PORT } else { 8100 }

if (-not (Test-Path -LiteralPath $python)) {
  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
  if (-not $pythonCommand) {
    throw "Python is not installed or available on PATH. Install Python 3.11 or newer."
  }
  $python = $pythonCommand.Source
}

if (Test-Path -LiteralPath $serverEnv) {
  foreach ($line in Get-Content -LiteralPath $serverEnv) {
    if ($line -match '^\s*AI_ENGINE_API_KEY=(.*)$' -and -not $env:AI_ENGINE_API_KEY) {
      $env:AI_ENGINE_API_KEY = $Matches[1].Trim().Trim('"').Trim("'")
    }
  }
}
if (-not $env:AI_ENGINE_API_KEY) {
  throw "AI_ENGINE_API_KEY is missing. Configure it in server\.env before starting the AI Engine."
}

$listeners = netstat.exe -ano -p tcp | Select-String "^\s*TCP\s+\S+:$port\s+\S+\s+LISTENING\s+(\d+)\s*$"
foreach ($listener in $listeners) {
  $ownerPid = [int]$listener.Matches[0].Groups[1].Value
  Write-Host "Stopping stale AI Engine process on port $port (PID $ownerPid)..."
  taskkill.exe /PID $ownerPid /T /F | Out-Null
}

Push-Location $PSScriptRoot
try {
  & $python "start.py"
} finally {
  Pop-Location
}
