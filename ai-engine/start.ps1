$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$serverEnv = Join-Path (Split-Path -Parent $PSScriptRoot) "server\.env"

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

$demoDataset = Join-Path $projectRoot "data\prysm-demo-v2"
$demoModels = Join-Path $PSScriptRoot "runs\demo-v2-build\model_bundle.json"
if ((Test-Path -LiteralPath $demoDataset) -and (Test-Path -LiteralPath $demoModels)) {
  $env:PRYSM_DATASET = $demoDataset
  $env:PRYSM_MODELS = $demoModels
}

& $python (Join-Path $PSScriptRoot "start.py")
