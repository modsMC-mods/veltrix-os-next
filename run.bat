@echo off
setlocal
cd /d "%~dp0"
echo Starting VELTRIX OS Next...
where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 goto no_python
  set PY=python
) else (
  set PY=py -3
)
if not exist .venv\Scripts\python.exe (
  echo Creating virtual environment...
  %PY% -m venv .venv
  if errorlevel 1 goto failed
)
call .venv\Scripts\activate.bat
echo Installing/checking dependencies...
python -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto failed
echo Launching desktop...
python -m veltrix
if errorlevel 1 goto failed
echo VELTRIX exited normally.
pause
exit /b 0
:no_python
echo Python 3 was not found. Install Python 3.10+ from https://www.python.org/downloads/ and enable Add Python to PATH.
goto pause_error
:failed
echo.
echo VELTRIX failed to start. Read the error above. A startup log may be at %%USERPROFILE%%\.local\state\veltrix-os\startup.log
:pause_error
pause
exit /b 1
