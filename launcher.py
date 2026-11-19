import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"


def start_veltrix():
    python = str(PYTHON if PYTHON.exists() else sys.executable)
    try:
        subprocess.Popen(
            [python, "-m", "veltrix"],
            cwd=ROOT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
        root.destroy()
    except Exception as exc:
        messagebox.showerror("Błąd VELTRIX", str(exc))


root = tk.Tk()
root.title("VELTRIX OS")
root.geometry("360x220")
root.resizable(False, False)

style = {"font": ("Segoe UI", 12)}
tk.Label(root, text="VELTRIX OS", font=("Segoe UI", 22, "bold")).pack(pady=(35, 20))
tk.Button(root, text="START", width=16, height=2, command=start_veltrix).pack()
tk.Label(root, text="Kliknij START, aby uruchomić VELTRIX", **style).pack(pady=12)

root.mainloop()
