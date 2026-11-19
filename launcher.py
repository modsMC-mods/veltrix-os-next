"""Small Windows-friendly launcher that installs dependencies and reports errors."""
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
        window.title("VELTRIX OS")
        window.geometry("380x250")
        window.resizable(False, False)
        window.configure(bg="#0b1020")

        tk.Label(window, text="VELTRIX OS", bg="#0b1020", fg="#69a5ff",
                 font=("Segoe UI", 23, "bold")).pack(pady=(32, 12))
        self.status = tk.Label(window, text="Gotowy do uruchomienia", bg="#0b1020",
                               fg="white", font=("Segoe UI", 10), wraplength=330)
        self.status.pack(pady=8)
        self.start_button = tk.Button(window, text="START", width=18, height=2,
                                      font=("Segoe UI", 12, "bold"), command=self.start)
        self.start_button.pack(pady=12)
        tk.Label(window, text="Przy pierwszym uruchomieniu może pobrać wymagane biblioteki.",
                 bg="#0b1020", fg="#9ba9c7", font=("Segoe UI", 9),
                 wraplength=340).pack(pady=5)

    def set_status(self, text):
        self.window.after(0, lambda: self.status.config(text=text))

    def start(self):
        self.start_button.config(state="disabled")
        self.set_status("Przygotowuję Pythona i wymagane biblioteki…")
        threading.Thread(target=self._prepare_and_run, daemon=True).start()

    def _prepare_and_run(self):
        try:
            with LOG_FILE.open("w", encoding="utf-8") as log:
                log.write("VELTRIX launcher log\n")
                log.flush()
                if not VENV_PYTHON.exists():
                    self.set_status("Tworzę środowisko Pythona…")
                    result = subprocess.run(
                        [sys.executable, "-m", "venv", str(ROOT / ".venv")],
                        cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, text=True,
                    )
                    if result.returncode:
                        raise RuntimeError("Nie udało się utworzyć środowiska Pythona.")

                self.set_status("Sprawdzam i instaluję biblioteki (może to chwilę potrwać)…")
                result = subprocess.run(
                    [str(VENV_PYTHON), "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")],
                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, text=True,
                )
                if result.returncode:
                    raise RuntimeError("Instalacja bibliotek nie powiodła się.")

                self.set_status("Uruchamiam VELTRIX OS…")
                log.write("\n--- VELTRIX output ---\n")
                log.flush()
                result = subprocess.run(
                    [str(VENV_PYTHON), "-m", "veltrix"], cwd=ROOT,
                    stdout=log, stderr=subprocess.STDOUT, text=True,
                )
                if result.returncode:
                    raise RuntimeError(f"VELTRIX zakończył działanie z kodem {result.returncode}.")
            self.window.after(0, lambda: self.status.config(text="VELTRIX został zamknięty."))
        except Exception as exc:
            self.window.after(0, lambda error=str(exc): self._show_error(error))
        finally:
            self.window.after(0, lambda: self.start_button.config(state="normal"))

    def _show_error(self, error):
        self.status.config(text="Nie udało się uruchomić VELTRIX.")
        messagebox.showerror(
            "Błąd uruchamiania VELTRIX",
            f"{error}\n\nLog błędu:\n{LOG_FILE}\n\nOtwórz log i prześlij jego treść, jeśli problem będzie się powtarzał.",
            parent=self.window,
        )


if __name__ == "__main__":
    root = tk.Tk()
    Launcher(root)
    root.mainloop()
