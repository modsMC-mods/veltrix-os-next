@echo off
setlocal
set "VELTRIX_ROOT=%~dp0"
cd /d "%VELTRIX_ROOT%"
if not exist ".venv\Scripts\python.exe" (
  echo VELTRIX is not installed yet. Run install-command.bat first, or install dependencies with:
  echo   py -3 -m pip install -r requirements.txt
  exit /b 2
)
"%VELTRIX_ROOT%.venv\Scripts\python.exe" -m veltrix %*
exit /b %ERRORLEVEL%
