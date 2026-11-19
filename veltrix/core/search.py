from pathlib import Path

def search(root, query, limit=100):
    root, query = Path(root).expanduser(), query.lower()
    if not root.exists(): return []
    return [p for p in root.rglob("*") if query in p.name.lower()][:limit]
