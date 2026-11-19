# VELTRIX Desktop

VELTRIX is a user-space desktop application with an Ubuntu/Mint-inspired interface. It runs **on top of** Windows or Linux; it is not an operating system, and it cannot provide every Windows 11, Linux Mint, or Ubuntu feature or replace their kernel, login screen, drivers, system settings, or desktop shell.

## Start on Windows

Install Python 3.10+ and enable **Add python.exe to PATH**. Extract the ZIP and double-click `launcher.bat`; press **START**. On first run it creates a virtual environment and installs the listed Python packages. You can also use `run.bat`.

## Start on Linux

```bash
chmod +x run.sh
./run.sh
```

## Included desktop features

- Desktop-style home screen, navigation sidebar, bottom taskbar, live clock, and dark/light appearance.
- File manager for browsing the current user's accessible files, opening files with host applications, navigating folders, and creating folders.
- Basic terminal that runs commands as the logged-in user in the current folder. It does not elevate privileges. Only enter commands you understand.
- Gaming Hub with Steam game discovery/launch, performance readings, and informational Linux gaming-tool checks.
- Basic host system and memory/CPU information.

These features use the host operating system for file permissions, default applications, terminal shell, drivers, networking, and other system services. VELTRIX does not make privileged or silent system changes.
