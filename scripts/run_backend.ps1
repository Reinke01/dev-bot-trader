param(
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Repo root (scripts is in repo/scripts)
$RepoRoot = (Resolve-Path "$PSScriptRoot\.." ).Path

# Candidate folders that may contain the backend source
$candidates = @(
  Join-Path $RepoRoot "backend",
  Join-Path $RepoRoot "dev-bot-trader-main",
  Join-Path $RepoRoot "devbot-trader-main",
  Join-Path $RepoRoot "."
)

$found = $null
foreach ($c in $candidates) {
  if (Test-Path (Join-Path $c "src/api/main.py")) { $found = $c; break }
}

if (-not $found) {
  Write-Host "Não foi encontrado 'src/api/main.py' nas pastas esperadas. Procure manualmente e ajuste o script." -ForegroundColor Yellow
  throw "Backend source (src/api/main.py) não encontrado"
}

# Work inside the project folder that contains the API
Set-Location $found

# venv path inside the chosen project
$venv = Join-Path $found ".venv"
$activate = Join-Path $venv "Scripts\Activate.ps1"

if (!(Test-Path $activate)) {
  python -m venv $venv
}

. $activate

python -m pip install -U pip

# Install requirements from the chosen project if present, otherwise fallback to dev-bot-trader-main requirements
$req = Join-Path $found "requirements.txt"
if (Test-Path $req) {
  pip install -r $req
} else {
  $fallback = Join-Path $RepoRoot "dev-bot-trader-main\requirements.txt"
  if (Test-Path $fallback) {
    pip install -r $fallback
  } else {
    Write-Host "requirements.txt não encontrado; instalando fallback uvicorn[standard]" -ForegroundColor Yellow
    pip install "uvicorn[standard]"
  }
}

# Ensure uvicorn is available
python -c "import uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
  pip install "uvicorn[standard]"
}

$srcDir = Join-Path $found "src"
Write-Host "Iniciando API em http://127.0.0.1:$Port (app-dir: $srcDir)"
python -m uvicorn api.main:app --reload --app-dir $srcDir --host 127.0.0.1 --port $Port
