@echo off
setlocal
cd /d "%~dp0"
echo Starting VELTRIX Desktop...
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3 was not found. Install Python and enable Add Python to PATH.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m veltrix.apps.desktop
if errorlevel 1 goto failed
exit /b 0
:failed
echo VELTRIX could not start. Check the error above.
pause
exit /b 1
