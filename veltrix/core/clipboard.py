from collections import deque
_history = deque(maxlen=50)
def remember(text):
    if text and (not _history or _history[-1] != text): _history.append(text)
def history(): return list(_history)
