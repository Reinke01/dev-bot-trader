# Robust Run frontend (PowerShell)
# Finds repo root (folder containing `devbot-trader-dashboard`), installs deps if needed, and runs Vite.

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
$dir = $scriptDir
while (-not (Test-Path (Join-Path $dir 'devbot-trader-dashboard'))) {
	$parent = Split-Path $dir -Parent
	if ($parent -eq $dir) { Write-Error "Repository root with 'devbot-trader-dashboard' not found."; exit 1 }
	$dir = $parent
}
$RepoRoot = $dir
$Frontend = Join-Path $RepoRoot 'devbot-trader-dashboard'
Push-Location $Frontend

if (-not (Test-Path (Join-Path $Frontend 'node_modules'))) {
	Write-Host "Installing frontend dependencies (npm install)"
	npm install
}

npm run dev -- --port 8080

Pop-Location
