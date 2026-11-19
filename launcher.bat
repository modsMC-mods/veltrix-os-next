@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Nie znaleziono Pythona. Zainstaluj Python 3.10+ i zaznacz Add Python to PATH.
  pause
  exit /b 1
)
py launcher.py
if errorlevel 1 (
  echo Launcher nie mógł wystartować. Jeśli py jest zainstalowany, uruchom:
  echo   py launcher.py
  pause
  exit /b 1
)
