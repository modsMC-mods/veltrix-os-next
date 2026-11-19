# VELTRIX Desktop

Windows-inspired desktop application for Windows and Linux. It runs as a normal user-space app on the host OS; it is not an operating-system replacement.

## Start

**Windows:** install Python 3.10+, enable **Add python.exe to PATH**, extract the ZIP, run `launcher.bat`, then click **START**. On first run the launcher creates `.venv` and installs dependencies. PyQt WebEngine is included for the built-in browser.

**Linux:** `chmod +x run.sh && ./run.sh`

## Apps and desktop tools

- Desktop wallpaper, shortcuts, Start menu, search box, taskbar, clock, CPU/RAM status, and light/dark theme.
- Built-in Chromium browser window powered by Qt WebEngine: multiple tabs, address/search bar, back/forward, reload, home, and shortcuts (`Ctrl+L`, `Ctrl+T`, `Ctrl+W`).
- File Explorer with folder navigation, visible-file filtering, details, open-with-host-app, create folder/file, `Alt+Up`, `Ctrl+L`, and `F5`.
- Terminal with `/help` built-ins: `/clear`, `/pwd`, `/ls`, `/cd`, `/open`, `/explorer`, `/browser`, `/date`, `/time`, `/whoami`, `/system`, `/cpu`, `/ram`, `/disk`, `/ip`, `/find`, `/mkdir`, `/touch`, `/theme`, and `/apps`. Other commands run in the host shell as the current user; enter only commands you understand.
- Gaming Hub launch, host system information, and quick app search.

VELTRIX uses the host OS for permissions, network, drivers, and services. It does not silently change system settings or elevate privileges.
