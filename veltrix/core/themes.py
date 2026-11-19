import json
from pathlib import Path

def import_theme(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "bg" not in data or "accent" not in data: raise ValueError("Nieprawidłowy motyw")
    return data
