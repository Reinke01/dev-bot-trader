# Robust Run backend API (PowerShell)
# Finds repository root (folder containing `src`), ensures a local .venv,
# activates it, installs requirements if missing, and starts Uvicorn.

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition }
$dir = $scriptDir
$dir = $scriptDir
while (-not (Test-Path (Join-Path $dir 'src') -and Test-Path (Join-Path $dir 'requirements.txt'))) {
	$parent = Split-Path $dir -Parent
	if ($parent -eq $dir) { Write-Error "Repository root with 'src' not found."; exit 1 }
	$dir = $parent
}
$RepoRoot = $dir
Push-Location $RepoRoot

if (-not (Test-Path "$RepoRoot\.venv")) {
	Write-Host "Creating virtual environment at $RepoRoot\.venv"
	python -m venv .venv
}

. "$RepoRoot\.venv\Scripts\Activate.ps1"


if (Test-Path "$RepoRoot\requirements.txt") {
	pip install -U pip
	pip install -r requirements.txt
	if ($LASTEXITCODE -ne 0) {
		Write-Host "pip install -r requirements.txt failed. Installing fallback uvicorn[standard]"
		pip install "uvicorn[standard]"
	}
} else {
	Write-Host "requirements.txt not found in $RepoRoot — installing uvicorn fallback"
	pip install "uvicorn[standard]"
}

# Ensure uvicorn is importable, otherwise install fallback
python - <<'PY'
try:
	import uvicorn
except Exception:
	import sys, subprocess
	subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'uvicorn[standard]'])
PY

# Use python -m uvicorn to avoid broken launcher pointing to old absolute paths
python -m uvicorn api.main:app --reload --app-dir src --host 127.0.0.1 --port 8000

Pop-Location
