@echo off
setlocal
REM Add this repository's launcher folder to the current user's PATH, then use `veltrix` in a new CMD.
set "VELTRIX_BIN=%LOCALAPPDATA%\Programs\VELTRIX\bin"
if not exist "%VELTRIX_BIN%" mkdir "%VELTRIX_BIN%"
copy /Y "%~dp0veltrix.cmd" "%VELTRIX_BIN%\veltrix.cmd" >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=[Environment]::GetEnvironmentVariable('Path','User'); $d='%VELTRIX_BIN%'; if (($p -split ';') -notcontains $d) { [Environment]::SetEnvironmentVariable('Path', (($p.TrimEnd(';') + ';' + $d).Trim(';')), 'User') }"
if errorlevel 1 (
  echo Could not update your user PATH. You can still run veltrix.cmd from this folder.
  pause
  exit /b 1
)
echo VELTRIX command installed: %VELTRIX_BIN%\veltrix.cmd
echo Close and reopen CMD, then type: veltrix
echo You can also start it now with: "%VELTRIX_BIN%\veltrix.cmd"
pause
