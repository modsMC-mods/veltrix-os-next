# VELTRIX PLAY

VELTRIX PLAY is an Ubuntu-inspired gaming dashboard for an existing Windows or Linux computer (it is not a Linux distribution or kernel).

## Windows setup

1. Install Python 3.10+ and select **Add python.exe to PATH**.
2. Extract the ZIP, then double-click `launcher.bat`.
3. Click **START**. The launcher creates its virtual environment, installs requirements and opens the gaming dashboard. First start needs an internet connection to install dependencies.

## Gaming features

- Dark neon dashboard with overview, game library, live performance page and gaming setup checks.
- Add a local game executable; the library is saved in `~/.veltrix/games.json`.
- Scan local Steam libraries for installed game manifests and launch them through Steam.
- Display CPU and memory utilization locally using psutil.
- On Linux, detect Steam, GameMode and MangoHud when their commands are available. Checks are informational; VELTRIX does not make privileged or silent system changes.

The Linux launcher is `./run.sh` (make executable with `chmod +x run.sh`). Steam, GameMode, MangoHud and hardware support are separate system components and may need to be installed using your distribution's trusted package sources.
