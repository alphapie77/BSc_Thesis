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
        throw "Python environment পাওয়া যায়নি: $demoPython"
    }
    if (-not (Test-Path -LiteralPath $demoEnv)) {
        throw ".env পাওয়া যায়নি। Repository root-এ GOOGLE_API_KEY সহ .env রাখুন।"
    }
    if (-not (Select-String -LiteralPath $demoEnv -Pattern '^GOOGLE_API_KEY=.+$' -Quiet)) {
        throw ".env-এ GOOGLE_API_KEY পাওয়া যায়নি বা value খালি।"
    }
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm পাওয়া যায়নি। Node.js install করে আবার চালান।"
    }

    & $demoPython -c "import fastapi" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FastAPI প্রথমবারের জন্য install হচ্ছে..." -ForegroundColor Yellow
        & $demoPython -m pip install fastapi
        if ($LASTEXITCODE -ne 0) {
            throw "FastAPI install ব্যর্থ হয়েছে।"
        }
    }

    if (-not (Test-Path -LiteralPath (Join-Path $demoInterface "node_modules"))) {
        Write-Host "Frontend dependencies প্রথমবারের জন্য install হচ্ছে..." -ForegroundColor Yellow
        Push-Location -LiteralPath $demoInterface
        try {
            & npm install
            if ($LASTEXITCODE -ne 0) {
                throw "npm install ব্যর্থ হয়েছে।"
            }
        }
        finally {
            Pop-Location
        }
    }

    Remove-Item -LiteralPath $demoBackendLog, $demoBackendErrorLog, $demoFrontendLog, $demoFrontendErrorLog -Force -ErrorAction SilentlyContinue

    Write-Host "Backend চালু হচ্ছে..." -ForegroundColor Cyan
    $demoBackend = Start-Process -FilePath $demoPython `
        -ArgumentList "-m", "uvicorn", "src.demo.api:app", "--host", "127.0.0.1", "--port", "8000" `
        -WorkingDirectory $demoRoot -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $demoBackendLog -RedirectStandardError $demoBackendErrorLog

    $backendReady = $false
    foreach ($attempt in 1..180) {
        if ($demoBackend.HasExited) {
            throw "Backend চালু হয়নি। Log: $demoBackendLog"
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
        throw "Backend ৩ মিনিটের মধ্যে ready হয়নি। Log: $demoBackendLog"
    }

    Write-Host "Interface চালু হচ্ছে..." -ForegroundColor Cyan
    $demoFrontend = Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" `
        -WorkingDirectory $demoInterface -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput $demoFrontendLog -RedirectStandardError $demoFrontendErrorLog

    $frontendReady = $false
    foreach ($attempt in 1..120) {
        if ($demoFrontend.HasExited) {
            throw "Interface চালু হয়নি। Log: $demoFrontendLog"
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
        throw "Interface ২ মিনিটের মধ্যে ready হয়নি। Log: $demoFrontendLog"
    }

    Write-Host "`nDemo ready: http://localhost:3000" -ForegroundColor Green
    Write-Host "এই window খোলা রাখুন। বন্ধ করতে Ctrl+C চাপুন।"
    Start-Process "http://localhost:3000"

    while (-not $demoBackend.HasExited -and -not $demoFrontend.HasExited) {
        Start-Sleep -Seconds 2
    }
    throw "একটি service অপ্রত্যাশিতভাবে বন্ধ হয়েছে। Logs: $demoBackendLog এবং $demoFrontendLog"
}
catch {
    Write-Host "`nDemo চালু করা যায়নি: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "বন্ধ করতে Enter চাপুন।"
    Read-Host | Out-Null
}
finally {
    Stop-DemoProcess $demoFrontend
    Stop-DemoProcess $demoBackend
}
