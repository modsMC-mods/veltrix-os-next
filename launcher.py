"""Small Windows-friendly launcher that prepares and starts VELTRIX Desktop."""
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
LOG_FILE = ROOT / "veltrix-launcher.log"


class Launcher:
    def __init__(self, window):
        self.window = window
        window.title("VELTRIX")
        window.geometry("390x265")
        window.resizable(False, False)
        window.configure(bg="#101319")
        tk.Label(window, text="V/ELTRIX", bg="#101319", fg="#a6ff00",
                 font=("Segoe UI", 25, "bold")).pack(pady=(30, 10))
        self.status = tk.Label(window, text="Pulpit gotowy do uruchomienia", bg="#101319",
                               fg="white", font=("Segoe UI", 10), wraplength=340)
        self.status.pack(pady=8)
        self.start_button = tk.Button(window, text="START", width=20, height=2,
                                      font=("Segoe UI", 12, "bold"), command=self.start)
        self.start_button.pack(pady=12)
        tk.Label(window, text="Pierwszy start przygotowuje środowisko i może chwilę potrwać.",
                 bg="#101319", fg="#a0a9b5", font=("Segoe UI", 9),
                 wraplength=350).pack(pady=5)

    def set_status(self, text):
        self.window.after(0, lambda: self.status.config(text=text))

    def start(self):
        self.start_button.config(state="disabled")
        self.set_status("Przygotowuję VELTRIX Desktop…")
        threading.Thread(target=self._prepare_and_run, daemon=True).start()

    def _prepare_and_run(self):
        try:
            with LOG_FILE.open("w", encoding="utf-8") as log:
                if not VENV_PYTHON.exists():
                    self.set_status("Tworzę środowisko Pythona…")
                    result = subprocess.run([sys.executable, "-m", "venv", str(ROOT / ".venv")], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                    if result.returncode:
                        raise RuntimeError("Nie udało się utworzyć środowiska Python.")
                self.set_status("Instaluję/sprawdzam wymagane pakiety…")
                result = subprocess.run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                if result.returncode:
                    raise RuntimeError("Instalacja pakietów nie powiodła się.")
                self.set_status("Uruchamiam pulpit…")
                log.write("\n--- VELTRIX Desktop output ---\n")
                log.flush()
                result = subprocess.run([str(VENV_PYTHON), "-m", "veltrix.apps.desktop"], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                if result.returncode:
                    raise RuntimeError(f"Pulpit zakończył działanie z kodem {result.returncode}.")
            self.window.after(0, lambda: self.status.config(text="Sesja VELTRIX została zamknięta."))
        except Exception as exc:
            self.window.after(0, lambda error=str(exc): self._show_error(error))
        finally:
            self.window.after(0, lambda: self.start_button.config(state="normal"))

    def _show_error(self, error):
        self.status.config(text="Nie udało się uruchomić pulpitu.")
        messagebox.showerror("Błąd VELTRIX", f"{error}\n\nLog:\n{LOG_FILE}", parent=self.window)


if __name__ == "__main__":
    root = tk.Tk()
    Launcher(root)
    root.mainloop()
