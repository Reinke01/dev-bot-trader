param(
  [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path "$PSScriptRoot\..").Path
$backend = Join-Path $root "backend"

if (!(Test-Path $backend)) { throw "Pasta backend não encontrada em: $backend" }

Set-Location $backend

# venv dentro do backend (profissional)
$venv = Join-Path $backend ".venv"
$activate = Join-Path $venv "Scripts\Activate.ps1"

if (!(Test-Path $activate)) {
  python -m venv $venv
}

. $activate

python -m pip install -U pip

if (Test-Path (Join-Path $backend "requirements.txt")) {
  pip install -r requirements.txt
} else {
  throw "requirements.txt não encontrado no backend"
}

# garante uvicorn
python -c "import uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
  pip install "uvicorn[standard]"
}

Write-Host "Iniciando API em http://127.0.0.1:$Port ..."
python -m uvicorn api.main:app --reload --app-dir src --host 127.0.0.1 --port $Port
