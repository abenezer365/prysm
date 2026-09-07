$ErrorActionPreference = "Stop"
$python = Join-Path (Split-Path -Parent $PSScriptRoot) ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
  if (-not $pythonCommand) {
    throw "Python is not installed or available on PATH. Install Python 3.11 or newer."
  }
  $python = $pythonCommand.Source
}

& $python (Join-Path $PSScriptRoot "main.py")
