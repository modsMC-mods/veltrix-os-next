import json
from pathlib import Path

def set_offline(enabled=True):
    path = Path.home() / ".config" / "veltrix-os" / "offline.json"; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps({"offline": enabled}))
def is_offline():
    path = Path.home() / ".config" / "veltrix-os" / "offline.json"
    return path.exists() and json.loads(path.read_text()).get("offline", False)
