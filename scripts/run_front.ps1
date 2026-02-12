# Run frontend from repo root (PowerShell)
# Detects frontend folder (contains package.json), runs npm install if needed and starts Vite on port 8080

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
$dir = $scriptDir
$frontendDir = $null
while ($dir -and -not $frontendDir) {
    $candidates = Get-ChildItem -Path $dir -Directory -ErrorAction SilentlyContinue
    foreach ($c in $candidates) {
        if (Test-Path (Join-Path $c.FullName 'package.json')) {
            $frontendDir = $c.FullName
            break
        }
    }
    if (-not $frontendDir) {
        $parent = Split-Path $dir -Parent
        if ($parent -eq $dir) { break }
        $dir = $parent
    }
}

if (-not $frontendDir) {
    Write-Error "Frontend folder not found (looked for package.json)."
    exit 1
}

Write-Host "Frontend detected at: $frontendDir"
Push-Location $frontendDir

if (-not (Test-Path (Join-Path $frontendDir 'node_modules'))) {
    Write-Host "Installing frontend dependencies (npm install)"
    npm install
}

npm run dev -- --host --port 8080

Pop-Location
param(
  [int]$Port = 8080
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path "$PSScriptRoot\..").Path
$dash = Join-Path $root "dashboard"

if (!(Test-Path $dash)) { throw "Pasta dashboard não encontrada em: $dash" }

Set-Location $dash

if (!(Test-Path (Join-Path $dash "node_modules"))) {
  npm install
}

Write-Host "Iniciando Front em http://localhost:$Port ..."
npm run dev -- --host --port $Port
