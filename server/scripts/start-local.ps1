$ErrorActionPreference = 'Stop'
$serverRoot = Split-Path -Parent $PSScriptRoot
$projectRoot = Split-Path -Parent $serverRoot

function Read-EnvValue([string]$Path, [string]$Name) {
  $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match "^$Name=" } | Select-Object -Last 1
  if (-not $line) { return '' }
  return ($line -replace "^$Name=", '').Trim()
}

function Wait-Ready([string]$Name, [string]$Url, [int]$Attempts = 180) {
  for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
    try {
      $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2 -Headers @{ Authorization = "Bearer $env:AI_ENGINE_API_KEY" }
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

$env:AI_ENGINE_API_KEY = Read-EnvValue (Join-Path $serverRoot '.env') 'AI_ENGINE_API_KEY'
$demoDataset = Join-Path $projectRoot 'data\prysm-demo-v2'
$demoModels = Join-Path $projectRoot 'ai-engine\runs\demo-v2-build\model_bundle.json'
if ((Test-Path -LiteralPath $demoDataset) -and (Test-Path -LiteralPath $demoModels)) {
  $env:PRYSM_DATASET = $demoDataset
  $env:PRYSM_MODELS = $demoModels
}

function Start-Component([string]$Path) {
  Start-Process powershell.exe -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',("`"$Path`"") -WindowStyle Hidden
}
function Stop-Listener([int]$Port, [string]$Name) {
  $listeners = netstat.exe -ano -p tcp | Select-String "^\s*TCP\s+\S+:$Port\s+\S+\s+LISTENING\s+(\d+)\s*$"
  foreach ($listener in $listeners) {
    $ownerPid = [int]$listener.Matches[0].Groups[1].Value
    Write-Host "Restarting $Name on port $Port (stopping PID $ownerPid)..."
    taskkill.exe /PID $ownerPid /T /F | Out-Null
  }
}
Stop-Listener 8100 'AI Engine'
Start-Component (Join-Path $projectRoot 'ai-engine\start.ps1')
Wait-Ready 'AI Engine' 'http://127.0.0.1:8100/ready'

Stop-Listener 8200 'RAG'
Start-Component (Join-Path $projectRoot 'chatbot\start.ps1')
Wait-Ready 'RAG' 'http://127.0.0.1:8200/health'

& npm.cmd --prefix $serverRoot run build
Stop-Listener 4000 'Backend'
Start-Component (Join-Path $serverRoot 'start.ps1')
Wait-Ready 'Backend' 'http://127.0.0.1:4000/api/v1/health/ready'

Stop-Listener 5173 'Frontend'
Start-Component (Join-Path $projectRoot 'client\start.ps1')
Wait-Ready 'Frontend' 'http://127.0.0.1:5173/'
Write-Host 'Prysm is ready: UI http://127.0.0.1:5173/ | API http://127.0.0.1:4000/api/v1'
