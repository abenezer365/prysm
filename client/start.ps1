$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try { & npm.cmd run start } finally { Pop-Location }
