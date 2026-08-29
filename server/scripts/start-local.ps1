$ErrorActionPreference = 'Stop'
$serverRoot = Split-Path -Parent $PSScriptRoot
$projectRoot = Split-Path -Parent $serverRoot

function Read-EnvValue([string]$Path, [string]$Name) {
  $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match "^$Name=" } | Select-Object -Last 1
  if (-not $line) { return '' }
  return ($line -replace "^$Name=", '').Trim()
}

function Wait-Ready([string]$Name, [string]$Url, [int]$Attempts = 60) {
  for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
    try {
      $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2
      if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) { Write-Host "$Name ready: $Url"; return }
    } catch { Start-Sleep -Milliseconds 500 }
  }
  throw "$Name did not become ready: $Url"
}

$postgres = Get-Service -Name 'postgresql*' -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $postgres) { throw 'No local PostgreSQL Windows service was found.' }
if ($postgres.Status -ne 'Running') { Start-Service -Name $postgres.Name }

$backendRagKey = Read-EnvValue (Join-Path $serverRoot '.env') 'RAG_API_KEY'
$ragKey = Read-EnvValue (Join-Path $projectRoot 'chatbot\.env') 'RAG_API_KEY'
if (-not $backendRagKey -or -not $ragKey) { throw 'RAG_API_KEY must be configured in both server/.env and chatbot/.env before starting the integrated stack.' }
if ($backendRagKey -ne $ragKey) { throw 'RAG_API_KEY differs between server/.env and chatbot/.env. Configure the same internal-only value in both files.' }

Start-Process python -ArgumentList '-m','uvicorn','api.app:app','--host','127.0.0.1','--port','8100' -WorkingDirectory (Join-Path $projectRoot 'ai-engine') -WindowStyle Hidden
Wait-Ready 'AI Engine' 'http://127.0.0.1:8100/ready'

Start-Process python -ArgumentList '-m','uvicorn','main:app','--host','127.0.0.1','--port','8200' -WorkingDirectory (Join-Path $projectRoot 'chatbot') -WindowStyle Hidden
Wait-Ready 'RAG' 'http://127.0.0.1:8200/health'

& npm.cmd run build
Start-Process node -ArgumentList '--env-file=.env','dist/src/server.js' -WorkingDirectory $serverRoot -WindowStyle Hidden
Wait-Ready 'Backend' 'http://127.0.0.1:4000/api/v1/health/ready'
Write-Host 'Prysm local backend stack is ready. Frontend may connect to http://127.0.0.1:4000/api/v1.'
