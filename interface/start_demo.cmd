@echo off
set "DEMO_ROOT=%~dp0.."
if not exist "%DEMO_ROOT%\start_demo.ps1" (
  echo Demo launcher not found. Download the full repository; the interface folder alone is not runnable.
  pause
  exit /b 1
)
cd /d "%DEMO_ROOT%"
call "%DEMO_ROOT%\start_demo.cmd"
exit /b %ERRORLEVEL%
