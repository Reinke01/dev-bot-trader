# test_api.ps1
# Tests the backend API endpoints.

Write-Host "🔍 Testing Backend API..." -ForegroundColor Cyan

function Test-Endpoint($Name, $Method, $Url, $Body) {
    Write-Host "Testing $Name ($Url)..." -NoNewline
    try {
        if ($Method -eq "GET") {
            $Response = Invoke-RestMethod -Uri $Url -Method Get
        }
        else {
            $Response = Invoke-RestMethod -Uri $Url -Method Post -Body $Body -ContentType "application/json"
        }
        Write-Host " ✅ Success" -ForegroundColor Green
        return $Response
    }
    catch {
        Write-Host " ❌ Failed" -ForegroundColor Red
        Write-Host $_.Exception.Message
        return $null
    }
}

$BaseUrl = "http://127.0.0.1:8000"

# 1. Health Check
Test-Endpoint "Health Check" "GET" "$BaseUrl/health" $null

# 2. Opportunities
# Note: The existing endpoint is /api/v1/scanner/results as seen in src/api/routes/scanner.py
# The requirements ask for /api/v1/opportunities
Test-Endpoint "Opportunities" "GET" "$BaseUrl/api/v1/opportunities?tf=15&limit=10&universe=top20" $null

# 3. Analyze
# Note: Existing endpoint is /api/v1/analise/moeda/{simbolo}
# Requirements ask for POST /api/v1/analyze with body { "symbol":"ATOMUSDT", "tf":"15" }
$AnalyzeBody = @{
    symbol = "ATOMUSDT"
    tf     = "15"
} | ConvertTo-Json
Test-Endpoint "Analyze" "POST" "$BaseUrl/api/v1/analyze" $AnalyzeBody

Write-Host "🏁 Testing sequence finished." -ForegroundColor Cyan
