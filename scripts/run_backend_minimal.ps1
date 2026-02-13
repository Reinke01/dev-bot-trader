param(
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Repo root (scripts is in repo/scripts) - ensure a single string path
$RepoRoot = (Resolve-Path "$PSScriptRoot\.." | Select-Object -First 1).Path

# Candidate folders that may contain the backend source
$candidates = @(
  (Join-Path $RepoRoot "backend"),
  (Join-Path $RepoRoot "dev-bot-trader-main"),
  (Join-Path $RepoRoot "devbot-trader-main"),
  $RepoRoot
)

$found = $null
foreach ($c in $candidates) {
  if (Test-Path (Join-Path $c "src/api/main.py")) { $found = $c; break }
}

if (-not $found) {
  Write-Host "Não foi encontrado 'src/api/main.py' nas pastas esperadas. Procure manualmente e ajuste o script." -ForegroundColor Yellow
  throw "Backend source (src/api/main.py) não encontrado"
}

Set-Location $found

# venv path inside the chosen project
$venv = Join-Path $found ".venv"
$activate = Join-Path $venv "Scripts\Activate.ps1"

if (!(Test-Path $activate)) {
  python -m venv $venv
}

. $activate

python -m pip install -U pip

# Install minimal requirements for dev server
pip install "fastapi" "uvicorn[standard]" "python-dotenv"

$srcDir = Join-Path $found "src"
Write-Host "Starting minimal API server at http://127.0.0.1:$Port (app-dir: $srcDir)"
python -m uvicorn api.main:app --reload --app-dir $srcDir --host 127.0.0.1 --port $Port
