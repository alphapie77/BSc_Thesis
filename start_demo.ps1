$ErrorActionPreference = "Stop"

$demoRoot = $PSScriptRoot
$demoPython = Join-Path $demoRoot ".venv\Scripts\python.exe"
$demoInterface = Join-Path $demoRoot "interface"
$demoVinext = Join-Path $demoInterface "node_modules\.bin\vinext.cmd"
$demoPackageLock = Join-Path $demoInterface "package-lock.json"
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

    if (-not (Test-Path -LiteralPath $demoVinext)) {
        $nodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
        if ($null -eq $nodeCommand) {
            throw "Node.js not found. Install Node.js 22 or later and try again."
        }
        $nodeDirectory = Split-Path -Parent $nodeCommand.Source
        $npmCli = Join-Path $nodeDirectory "node_modules\npm\bin\npm-cli.js"
        if (-not (Test-Path -LiteralPath $npmCli)) {
            throw "npm CLI not found beside Node.js: $npmCli. Repair Node.js/npm and try again."
        }
        if (-not (Test-Path -LiteralPath $demoPackageLock)) {
            throw "Frontend lockfile not found: $demoPackageLock"
        }
        Write-Host "Frontend dependencies are missing or incomplete; restoring package-lock.json exactly..." -ForegroundColor Yellow
        Push-Location -LiteralPath $demoInterface
        try {
            $ErrorActionPreference = "Continue"
            & $nodeCommand.Source $npmCli ci
            $npmInstallExitCode = $LASTEXITCODE
            $ErrorActionPreference = $savedErrorPreference
            if ($npmInstallExitCode -ne 0) {
                throw "npm ci failed. Close any running demo/Node process that may lock interface\node_modules, then run start_demo.cmd again."
            }
        }
        finally {
            Pop-Location
        }
    }
    if (-not (Test-Path -LiteralPath $demoVinext)) {
        throw "Frontend dependency restore completed but Vinext is still missing: $demoVinext"
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
    $artifactsReady = $false
    foreach ($attempt in 1..60) {
        if ($null -ne $demoBackend -and $demoBackend.HasExited) {
            throw "Backend stopped while loading artifacts. Log: $demoBackendErrorLog"
        }
        try {
            $readiness = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/ready" -TimeoutSec 15
            if ($readiness.status -eq "ready" -and
                $readiness.backend_initialized -eq $true -and
                $readiness.verifier_b_loaded -eq $false) {
                $artifactsReady = $true
                break
            }
        }
        catch {
            # A 503 response means the one-time CPU artifact load is still in
            # progress. Retry within the bounded five-minute startup window.
        }
        Start-Sleep -Seconds 5
    }
    if (-not $artifactsReady) {
        throw "Backend artifacts were not ready within 5 minutes. Log: $demoBackendErrorLog"
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
