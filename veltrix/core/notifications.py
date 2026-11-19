from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Notification:
    title: str
    message: str
    created_at: str
    level: str = "info"

_notifications = []

def notify(title, message, level="info"):
    item = Notification(title, message, datetime.now().isoformat(timespec="seconds"), level)
    _notifications.append(item)
    return item

def recent(limit=50):
    return _notifications[-limit:]
