$ErrorActionPreference = "Stop"

$demoRoot = $PSScriptRoot
$demoPython = Join-Path $demoRoot ".venv\Scripts\python.exe"
$demoInterface = Join-Path $demoRoot "interface"
$demoEnv = Join-Path $demoRoot ".env"
$demoBackendLog = Join-Path $env:TEMP "thesis-demo-backend.log"
$demoBackendErrorLog = Join-Path $env:TEMP "thesis-demo-backend-error.log"
$demoFrontendLog = Join-Path $env:TEMP "thesis-demo-frontend.log"
$demoFrontendErrorLog = Join-Path $env:TEMP "thesis-demo-frontend-error.log"
$demoBackend = $null
$demoFrontend = $null

function Stop-DemoProcess {
    param($Process)
    if ($null -ne $Process -and -not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
    }
}

try {
    Set-Location -LiteralPath $demoRoot

    if (-not (Test-Path -LiteralPath $demoPython)) {
        throw "Python environment not found: $demoPython"
    }
    if (-not (Test-Path -LiteralPath $demoEnv)) {
        throw ".env not found. Put .env with GOOGLE_API_KEY in the repository root."
    }
    if (-not (Select-String -LiteralPath $demoEnv -Pattern '^GOOGLE_API_KEY=.+$' -Quiet)) {
        throw "GOOGLE_API_KEY is missing or empty in .env."
    }
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm not found. Install Node.js and try again."
    }

    & $demoPython -c "import fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing the missing FastAPI dependency..." -ForegroundColor Yellow
        & $demoPython -m pip install fastapi
        if ($LASTEXITCODE -ne 0) {
            throw "FastAPI installation failed."
        }
    }

    if (-not (Test-Path -LiteralPath (Join-Path $demoInterface "node_modules"))) {
        Write-Host "Installing frontend dependencies for the first run..." -ForegroundColor Yellow
        Push-Location -LiteralPath $demoInterface
        try {
            & npm install
            if ($LASTEXITCODE -ne 0) {
                throw "npm install failed."
            }
        }
        finally {
            Pop-Location
        }
    }

    Remove-Item -LiteralPath $demoBackendLog, $demoBackendErrorLog, $demoFrontendLog, $demoFrontendErrorLog -Force -ErrorAction SilentlyContinue

    Write-Host "Starting backend..." -ForegroundColor Cyan
    $demoBackend = Start-Process -FilePath $demoPython `
        -ArgumentList "-m", "uvicorn", "src.demo.api:app", "--host", "127.0.0.1", "--port", "8000" `
        -WorkingDirectory $demoRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $demoBackendLog -RedirectStandardError $demoBackendErrorLog

    $backendReady = $false
    foreach ($attempt in 1..180) {
        if ($demoBackend.HasExited) {
            throw "Backend failed to start. Log: $demoBackendLog"
        }
        try {
            Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2 | Out-Null
            $backendReady = $true
            break
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $backendReady) {
        throw "Backend was not ready within 3 minutes. Log: $demoBackendLog"
    }

    Write-Host "Starting interface..." -ForegroundColor Cyan
    $demoFrontend = Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" `
        -WorkingDirectory $demoInterface -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $demoFrontendLog -RedirectStandardError $demoFrontendErrorLog

    $frontendReady = $false
    foreach ($attempt in 1..120) {
        if ($demoFrontend.HasExited) {
            throw "Interface failed to start. Log: $demoFrontendLog"
        }
        try {
            Invoke-WebRequest -Uri "http://127.0.0.1:3000" -UseBasicParsing -TimeoutSec 2 | Out-Null
            $frontendReady = $true
            break
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $frontendReady) {
        throw "Interface was not ready within 2 minutes. Log: $demoFrontendLog"
    }

    Write-Host "`nDemo ready: http://localhost:3000" -ForegroundColor Green
    Write-Host "Keep this window open. Press Ctrl+C to stop both services."
    Start-Process "http://localhost:3000"

    while (-not $demoBackend.HasExited -and -not $demoFrontend.HasExited) {
        Start-Sleep -Seconds 2
    }
    throw "A service stopped unexpectedly. Logs: $demoBackendLog and $demoFrontendLog"
}
catch {
    Write-Host "`nDemo could not start: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press Enter to close."
    Read-Host | Out-Null
}
finally {
    Stop-DemoProcess $demoFrontend
    Stop-DemoProcess $demoBackend
}
