# VELTRIX Desktop

VELTRIX is a Windows-inspired user-space desktop for Windows/Linux; it is not an operating-system replacement.

## Start
Windows: install Python 3.10+, enable **Add python.exe to PATH**, extract the ZIP, run `launcher.bat`, click START. Linux: `chmod +x run.sh && ./run.sh`. First run installs PyQt6, Qt WebEngine, and psutil.

## Included apps
- Desktop, Start/search, taskbar, wallpaper, system status and theme switch.
- Built-in Qt WebEngine browser with tabs, address/search, back/forward and refresh.
- Explorer with current-folder filter, file/folder creation, metadata and open-with-host-app.
- Terminal `/help` includes built-in `/calc`, `/note`, `/clipboard`, `/uptime`, `/battery`, `/processes`, `/screenshot`, `/network`, `/which`, `/free`, plus existing `/pwd`, `/ls`, `/cd`, `/open`, `/browser`, `/system`, `/cpu`, `/ram`, `/disk`, `/ip`, `/find`, `/mkdir`, `/touch`, `/theme`, `/apps`. Other commands run as the current user.
- Local autosaving Notes, safe Calculator (no eval), read-only process monitor, screenshot saver, gaming dashboard.

See `FEATURE-ROADMAP-50.md` for a prioritized list of 50 potential additions. VELTRIX uses host OS permissions/services and does not elevate privileges or silently change system settings.
