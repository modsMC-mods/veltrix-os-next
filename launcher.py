import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

ROOT = Path(__file__).resolve().parent
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
LOG_FILE = ROOT / "veltrix-launcher.log"


def start_veltrix():
    start_button.config(state="disabled", text="URUCHAMIAM…")
    status.config(text="Sprawdzam środowisko i uruchamiam pulpit…")
    threading.Thread(target=launch_worker, daemon=True).start()


def launch_worker():
    try:
        python = PYTHON if PYTHON.exists() else Path(sys.executable)
        with LOG_FILE.open("w", encoding="utf-8") as log:
            if not PYTHON.exists():
                result = subprocess.run([sys.executable, "-m", "venv", str(ROOT / ".venv")], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                if result.returncode:
                    raise RuntimeError("Nie udało się utworzyć środowiska .venv.")
                python = PYTHON
            result = subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(ROOT / "requirements.txt")], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError("Instalowanie zależności nie powiodło się. Szczegóły są w logu.")
            log.write("\n--- VELTRIX Desktop ---\n")
            log.flush()
            process = subprocess.Popen([str(python), "-m", "veltrix.apps.desktop_plus"], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            try:
                code = process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                window.after(0, lambda: status.config(text="Pulpit uruchomiony. Możesz zamknąć to okno."))
                window.after(0, lambda: start_button.config(state="normal", text="URUCHOM PONOWNIE"))
                return
            if code:
                raise RuntimeError(f"Pulpit zakończył działanie z kodem {code}. Sprawdź log.")
        window.after(0, lambda: status.config(text="Sesja VELTRIX została zamknięta."))
    except Exception as error:
        window.after(0, lambda e=str(error): show_error(e))
    finally:
        window.after(0, lambda: start_button.config(state="normal", text="START"))


def show_error(error):
    status.config(text="Nie udało się uruchomić pulpitu.")
    messagebox.showerror("Błąd VELTRIX", f"{error}\n\nLog:\n{LOG_FILE}", parent=window)


window = tk.Tk()
window.title("VELTRIX")
window.geometry("480x300")
window.resizable(False, False)
window.configure(bg="#10141c")
tk.Label(window, text="V/ELTRIX", bg="#10141c", fg="#a6ff00", font=("Segoe UI", 28, "bold")).pack(pady=(35, 7))
tk.Label(window, text="DESKTOP • PLAY • CREATE", bg="#10141c", fg="#aab4c5", font=("Segoe UI", 10, "bold")).pack()
status = tk.Label(window, text="Gotowy do uruchomienia", bg="#10141c", fg="#f4f6fb", font=("Segoe UI", 10), wraplength=410)
status.pack(pady=(25, 12))
start_button = tk.Button(window, text="START", command=start_veltrix, bg="#a6ff00", fg="#11150b", relief="flat", font=("Segoe UI", 12, "bold"), width=22, height=2, cursor="hand2")
start_button.pack(pady=8)
tk.Label(window, text="Pierwszy start pobiera wymagane komponenty przeglądarki.", bg="#10141c", fg="#8795a4", font=("Segoe UI", 9)).pack(pady=8)
window.mainloop()
