# VELTRIX Desktop

VELTRIX is a user-space desktop application for Windows and Linux. It is not a kernel or operating-system replacement.

## Windows

1. Install Python 3.10+ and enable **Add python.exe to PATH**.
2. Extract the repository.
3. Double-click `launcher.bat`.
4. Press **START**. The launcher creates `.venv`, installs `PyQt6` and `psutil`, then starts the desktop.

If startup fails, press **OTWÓRZ LOG**. The launcher also writes `veltrix-launcher.log` in the repository folder.

## Linux

```bash
chmod +x run.sh
./run.sh
```

## Features

- Modern desktop home screen and taskbar.
- Local file manager with navigation and folder creation.
- Terminal running with the current user's permissions.
- Gaming Hub entry point.
- CPU/RAM monitoring and dark/light themes.
