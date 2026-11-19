import hashlib
import json
from pathlib import Path

USERS_FILE = Path.home() / ".config" / "veltrix-os" / "users.json"

def _hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_user(username, password):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    users = json.loads(USERS_FILE.read_text()) if USERS_FILE.exists() else {}
    if username in users: raise ValueError("Użytkownik już istnieje")
    users[username] = _hash(password); USERS_FILE.write_text(json.dumps(users), encoding="utf-8")

def authenticate(username, password):
    if not USERS_FILE.exists(): return False
    return json.loads(USERS_FILE.read_text()).get(username) == _hash(password)
