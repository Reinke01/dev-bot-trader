<#
Quick health checks for environment: python, pip, venv, uvicorn, backend src
#>
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path "$PSScriptRoot\.." ).Path
Write-Host "Repo root: $RepoRoot"

# python
Write-Host "Checking Python..."
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { Write-Host "python not found in PATH" -ForegroundColor Red; exit 1 }
python --version

# pip
Write-Host "Checking pip..."
python -m pip --version

# uvicorn
Write-Host "Checking uvicorn (in current environment)..."
python -c "import uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "uvicorn not installed in current Python - run scripts/run_backend.ps1 to create venv and install" -ForegroundColor Yellow }
else { Write-Host "uvicorn available" }

# find backend src
Write-Host "Looking for API source (src/api/main.py)"
$candidates = @(
  Join-Path $RepoRoot "backend",
  Join-Path $RepoRoot "dev-bot-trader-main",
  Join-Path $RepoRoot "devbot-trader-main"
)
$found = $null
foreach ($c in $candidates) { if (Test-Path (Join-Path $c "src/api/main.py")) { $found = $c; break } }
if ($found) { Write-Host "Found API in: $found" } else { Write-Host "API source not found in expected locations" -ForegroundColor Yellow }

Write-Host "Suggested commands to run backend (from repository root)"
Write-Host "  .\scripts\run_backend.ps1" -ForegroundColor Green
Write-Host "Suggested commands to run frontend (from repository root)"
Write-Host "  .\scripts\run_frontend.ps1" -ForegroundColor Green
