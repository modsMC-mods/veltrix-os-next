@echo off
setlocal
cd /d "%~dp0"
py launcher.py
if errorlevel 1 (
    echo Launcher nie mógł wystartować.
    echo Upewnij się, że Python 3.10 lub nowszy jest zainstalowany.
    echo.
    py --version
    pause
)
