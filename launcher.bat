@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
    echo Nie znaleziono polecenia py. Zainstaluj Python 3 i zaznacz Add Python to PATH.
    pause
    exit /b 1
)
py launcher.py
if errorlevel 1 (
    echo Launcher zakończył działanie z błędem.
    pause
)
