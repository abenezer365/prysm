$ErrorActionPreference = "Stop"
$python = Join-Path (Split-Path -Parent $PSScriptRoot) ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
  throw "Prysm virtual environment not found at $python"
}

Push-Location $PSScriptRoot
try {
  & $python "start.py"
} finally {
  Pop-Location
}
