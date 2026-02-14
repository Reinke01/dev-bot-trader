# setup_backend.ps1
# Creates venv, activates it, and installs minimal requirements.

$ProjectRoot = Get-Item $PSScriptRoot\..
$BackendDir = Join-Path $ProjectRoot.FullName "backend"
$VenvDir = Join-Path $BackendDir ".venv"

Write-Host "🚀 Setting up backend environment..." -ForegroundColor Cyan

if (!(Test-Path $BackendDir)) {
    Write-Error "Backend directory not found!"
    exit 1
}

# Create venv if it doesn't exist
if (!(Test-Path $VenvDir)) {
    Write-Host "📦 Creating virtual environment in $VenvDir..."
    python -m venv $VenvDir
} else {
    Write-Host "✅ Virtual environment already exists."
}

# Activate venv and install requirements
Write-Host "📥 Installing minimal requirements..."
$PipPath = Join-Path $VenvDir "Scripts\pip.exe"
$RequirementsPath = Join-Path $BackendDir "requirements.min.txt"

& $PipPath install -r $RequirementsPath

Write-Host "✅ Setup complete!" -ForegroundColor Green
