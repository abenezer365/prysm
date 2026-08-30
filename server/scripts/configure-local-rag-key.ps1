$ErrorActionPreference = 'Stop'

$serverRoot = Split-Path -Parent $PSScriptRoot
$projectRoot = Split-Path -Parent $serverRoot
$serverEnv = Join-Path $serverRoot '.env'
$chatEnv = Join-Path $projectRoot 'chatbot\.env'

function Read-EnvValue([string]$Path, [string]$Name) {
  $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match "^$Name=" } | Select-Object -Last 1
  if (-not $line) { return '' }
  return ($line -replace "^$Name=", '').Trim()
}

function Set-EnvValue([string]$Path, [string]$Name, [string]$Value) {
  $lines = @(Get-Content -LiteralPath $Path)
  $found = $false
  $updated = foreach ($line in $lines) {
    if ($line -match "^$Name=") {
      if (-not $found) { "$Name=$Value" }
      $found = $true
    } else { $line }
  }
  if (-not $found) { $updated += "$Name=$Value" }
  Set-Content -LiteralPath $Path -Value $updated -Encoding utf8
}

$serverKey = Read-EnvValue $serverEnv 'RAG_API_KEY'
$chatKey = Read-EnvValue $chatEnv 'RAG_API_KEY'

if ($serverKey -and $serverKey -eq $chatKey) {
  Write-Host 'RAG internal authentication is already configured consistently.'
  exit 0
}

$bytes = New-Object byte[] 48
$generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try { $generator.GetBytes($bytes) } finally { $generator.Dispose() }
$key = [Convert]::ToBase64String($bytes)
Set-EnvValue $serverEnv 'RAG_API_KEY' $key
Set-EnvValue $chatEnv 'RAG_API_KEY' $key
Write-Host 'Configured a matching internal RAG key in both uncommitted service environment files.'
