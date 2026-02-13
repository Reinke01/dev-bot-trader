param(
  [int]$Port = 5173
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path "$PSScriptRoot\.." ).Path

# Candidate frontend folders
$candidates = @(
  Join-Path $RepoRoot "devbot-trader-dashboard",
  Join-Path $RepoRoot "dashboard",
  Join-Path $RepoRoot "devbot-trader-main"
)

$found = $null
foreach ($c in $candidates) {
  if (Test-Path (Join-Path $c "package.json")) { $found = $c; break }
}

if (-not $found) { throw "Frontend (package.json) não encontrado em candidates: $($candidates -join ', ')" }

Set-Location $found

Write-Host "Frontend encontrado em: $found"

# Prefer bun if lock file exists
if (Test-Path "bun.lockb") {
  Write-Host "Usando bun (bun.lockb encontrado)"
  if (-not (Get-Command bun -ErrorAction SilentlyContinue)) { throw "bun não encontrado no PATH" }
  bun install
  bun dev --port $Port
} else {
  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw "npm não encontrado no PATH" }
  npm install
  npm run dev -- --port $Port
}
