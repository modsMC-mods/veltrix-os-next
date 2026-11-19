@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m veltrix.apps.desktop_plus
if errorlevel 1 goto failed
exit /b 0
:failed
echo VELTRIX could not start. Check the error above.
pause
exit /b 1
