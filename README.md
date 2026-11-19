# VELTRIX Desktop

VELTRIX is a polished, Windows-inspired desktop application for Windows and Linux. It runs as a normal user-space app on the host OS; it is not a replacement for Windows, Linux, their kernel, drivers, login manager, or system settings.

## Windows

1. Install Python 3.10+ and enable **Add python.exe to PATH**.
2. Extract the repository ZIP.
3. Double-click `launcher.bat` and click **START**. On first run it creates `.venv` and installs dependencies.

## Linux

```bash
chmod +x run.sh
./run.sh
```

## Desktop features

- Custom gradient wallpaper, desktop shortcuts, Start/app menu, taskbar, clock and live CPU/RAM status.
- Explorer window: browse folders, search the current directory, open files in host apps, create folders, and navigate with keyboard shortcuts.
- Terminal window runs commands with the current user's permissions.
- Gaming Hub, browser shortcut, system information, and dark/light appearance settings.

VELTRIX intentionally uses the host OS for real system services and permissions. It does not imitate or replace the Windows/Linux kernel or silently modify system settings.
