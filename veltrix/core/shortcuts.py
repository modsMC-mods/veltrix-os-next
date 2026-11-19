DEFAULT_SHORTCUTS = {"terminal": "Ctrl+Alt+T", "search": "Super+Space", "screenshot": "Print"}
def shortcuts(custom=None): return {**DEFAULT_SHORTCUTS, **(custom or {})}
