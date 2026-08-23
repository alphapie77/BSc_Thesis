$ErrorActionPreference = "Stop"

$demoRoot = $PSScriptRoot
$demoPython = Join-Path $demoRoot ".venv\Scripts\python.exe"
$demoInterface = Join-Path $demoRoot "interface"
$demoVinext = Join-Path $demoInterface "node_modules\.bin\vinext.cmd"
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
    $env:HF_HUB_OFFLINE = "1"
    $env:TRANSFORMERS_OFFLINE = "1"

    if (-not (Test-Path -LiteralPath $demoPython)) {
        throw "Python environment not found: $demoPython"
    }
    if (-not (Test-Path -LiteralPath $demoEnv)) {
        throw ".env not found. Put .env with GOOGLE_API_KEY in the repository root."
    }
    if (-not (Select-String -LiteralPath $demoEnv -Pattern '^GOOGLE_API_KEY=.+$' -Quiet)) {
        throw "GOOGLE_API_KEY is missing or empty in .env."
    }
    $savedErrorPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $demoPython -c "import fastapi" *> $null
    $fastApiCheckExitCode = $LASTEXITCODE
    $ErrorActionPreference = $savedErrorPreference
    if ($fastApiCheckExitCode -ne 0) {
        Write-Host "Installing the missing FastAPI dependency..." -ForegroundColor Yellow
        $ErrorActionPreference = "Continue"
        & $demoPython -m pip install fastapi
        $fastApiInstallExitCode = $LASTEXITCODE
        $ErrorActionPreference = $savedErrorPreference
        if ($fastApiInstallExitCode -ne 0) {
            throw "FastAPI installation failed."
        }
    }

    if (-not (Test-Path -LiteralPath (Join-Path $demoInterface "node_modules"))) {
        if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
            throw "npm not found. Install Node.js and try again."
        }
        & npm --version *> $null
        if ($LASTEXITCODE -ne 0) {
            throw "npm is installed but not working. Repair Node.js/npm and try again."
        }
        Write-Host "Installing frontend dependencies for the first run..." -ForegroundColor Yellow
        Push-Location -LiteralPath $demoInterface
        try {
            $ErrorActionPreference = "Continue"
            & npm install
            $npmInstallExitCode = $LASTEXITCODE
            $ErrorActionPreference = $savedErrorPreference
            if ($npmInstallExitCode -ne 0) {
                throw "npm install failed."
            }
        }
        finally {
            Pop-Location
        }
    }
    if (-not (Test-Path -LiteralPath $demoVinext)) {
        throw "Frontend runner not found: $demoVinext"
    }

    Remove-Item -LiteralPath $demoBackendLog, $demoBackendErrorLog, $demoFrontendLog, $demoFrontendErrorLog -Force -ErrorAction SilentlyContinue

    $backendReady = $false
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2 | Out-Null
        $backendReady = $true
        Write-Host "Using the backend already running on port 8000." -ForegroundColor Cyan
    }
    catch {
        Write-Host "Starting backend..." -ForegroundColor Cyan
        $demoBackend = Start-Process -FilePath $demoPython `
            -ArgumentList "-m", "uvicorn", "src.demo.api:app", "--host", "127.0.0.1", "--port", "8000" `
            -WorkingDirectory $demoRoot -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput $demoBackendLog -RedirectStandardError $demoBackendErrorLog

        foreach ($attempt in 1..180) {
            if ($demoBackend.HasExited) {
                throw "Backend failed to start. Logs: $demoBackendLog and $demoBackendErrorLog"
            }
            try {
                Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" -TimeoutSec 2 | Out-Null
                $backendReady = $true
                break
            }
            catch {
                Start-Sleep -Seconds 1
            }
        }
    }
    if (-not $backendReady) {
        throw "Backend was not ready within 3 minutes. Log: $demoBackendLog"
    }
    Write-Host "Loading R1 and verifier artifacts..." -ForegroundColor Cyan
    try {
        Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/ready" -TimeoutSec 300 | Out-Null
    }
    catch {
        throw "Backend artifacts failed readiness. Log: $demoBackendErrorLog"
    }

    $frontendReady = $false
    try {
        Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2 | Out-Null
        $frontendReady = $true
        Write-Host "Using the interface already running on port 3000." -ForegroundColor Cyan
    }
    catch {
        Write-Host "Starting interface..." -ForegroundColor Cyan
        $demoFrontend = Start-Process -FilePath $demoVinext -ArgumentList "dev" `
            -WorkingDirectory $demoInterface -WindowStyle Hidden -PassThru `
            -RedirectStandardOutput $demoFrontendLog -RedirectStandardError $demoFrontendErrorLog

        foreach ($attempt in 1..120) {
            if ($demoFrontend.HasExited) {
                throw "Interface failed to start. Logs: $demoFrontendLog and $demoFrontendErrorLog"
            }
            try {
                Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2 | Out-Null
                $frontendReady = $true
                break
            }
            catch {
                Start-Sleep -Seconds 1
            }
        }
    }
    if (-not $frontendReady) {
        throw "Interface was not ready within 2 minutes. Log: $demoFrontendLog"
    }

    Write-Host "`nDemo ready: http://localhost:3000" -ForegroundColor Green
    Write-Host "Keep this window open. Press Ctrl+C to stop both services."
    try {
        Start-Process "http://localhost:3000" -ErrorAction Stop
    }
    catch {
        Write-Host "Browser could not open automatically. Open http://localhost:3000 manually." -ForegroundColor Yellow
    }

    while (($null -eq $demoBackend -or -not $demoBackend.HasExited) -and
           ($null -eq $demoFrontend -or -not $demoFrontend.HasExited)) {
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
