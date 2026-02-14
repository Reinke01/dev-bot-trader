# run_backend.ps1
# Runs the backend API using uvicorn.

$ProjectRoot = Get-Item $PSScriptRoot\..
$BackendDir = Join-Path $ProjectRoot.FullName "backend"
$VenvDir = Join-Path $BackendDir ".venv"
$PythonPath = Join-Path $VenvDir "Scripts\python.exe"
$UvicornPath = Join-Path $VenvDir "Scripts\uvicorn.exe"

Write-Host "🔥 Starting backend API..." -ForegroundColor Cyan

if (!(Test-Path $UvicornPath)) {
    Write-Host "⚠️ Uvicorn not found. Running setup first..." -ForegroundColor Yellow
    & (Join-Path $PSScriptRoot "setup_backend.ps1")
}

# Add backend\src to PYTHONPATH
$env:PYTHONPATH = Join-Path $BackendDir "src"

# Run uvicorn from the backend directory
Set-Location $BackendDir
& $UvicornPath src.api.main:app --host 127.0.0.1 --port 8000 --reload
