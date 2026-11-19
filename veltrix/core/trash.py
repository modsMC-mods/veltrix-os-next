import shutil
from pathlib import Path

TRASH = Path.home() / ".local" / "share" / "Trash" / "files"

def move_to_trash(path):
    TRASH.mkdir(parents=True, exist_ok=True); source = Path(path); target = TRASH / source.name; shutil.move(str(source), str(target)); return target

def list_trash():
    return sorted(TRASH.iterdir()) if TRASH.exists() else []
