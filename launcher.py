"""Modern VELTRIX launcher for Windows and Linux."""
import subprocess
import sys
import threading
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

ROOT = Path(__file__).resolve().parent
IS_WINDOWS = sys.platform == "win32"
VENV_PYTHON = ROOT / (".venv/Scripts/python.exe" if IS_WINDOWS else ".venv/bin/python")
LOG_FILE = ROOT / "veltrix-launcher.log"


class Launcher:
    def __init__(self, window):
        self.window = window
        self.window.title("VELTRIX")
        self.window.geometry("520x330")
        self.window.minsize(520, 330)
        self.window.configure(bg="#070a0f")

        top = tk.Frame(window, bg="#070a0f", height=8)
        top.pack(fill="x")
        accent = tk.Frame(window, bg="#a6ff00", height=3)
        accent.pack(fill="x", padx=44)

        main = tk.Frame(window, bg="#070a0f")
        main.pack(fill="both", expand=True, padx=44, pady=(28, 22))

        tk.Label(main, text="V/ELTRIX", bg="#070a0f", fg="#a6ff00",
                 font=("Segoe UI", 30, "bold")).pack(anchor="w")
        tk.Label(main, text="DESKTOP SYSTEM", bg="#070a0f", fg="#8794a1",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 24))

        self.status = tk.Label(main, text="Wszystko gotowe do uruchomienia.",
                               bg="#070a0f", fg="#eef3f7",
                               font=("Segoe UI", 11), wraplength=430,
                               justify="left")
        self.status.pack(fill="x", pady=(0, 12))

        self.progress = tk.Label(main, text="", bg="#070a0f", fg="#8794a1",
                                 font=("Segoe UI", 9), wraplength=430,
                                 justify="left")
        self.progress.pack(fill="x")

        controls = tk.Frame(main, bg="#070a0f")
        controls.pack(fill="x", pady=(24, 0))

        self.start_button = tk.Button(controls, text="START", bg="#a6ff00", fg="#0a0d08",
                                      activebackground="#c9ff61", activeforeground="#0a0d08",
                                      relief="flat", borderwidth=0, cursor="hand2",
                                      font=("Segoe UI", 13, "bold"), command=self.start,
                                      width=16, height=2)
        self.start_button.pack(side="left")

        self.log_button = tk.Button(controls, text="OTWÓRZ LOG", bg="#171d25", fg="#dce4ea",
                                    activebackground="#222b35", relief="flat", borderwidth=0,
                                    font=("Segoe UI", 9, "bold"), command=self.open_log,
                                    width=14, height=2)
        self.log_button.pack(side="right")

    def set_status(self, status, detail=""):
        self.window.after(0, lambda: (
            self.status.config(text=status),
            self.progress.config(text=detail),
        ))

    def open_log(self):
        if not LOG_FILE.exists():
            messagebox.showinfo("Log VELTRIX", "Nie ma jeszcze pliku logu.", parent=self.window)
            return
        try:
            LOG_FILE.resolve().open("r", encoding="utf-8")
            if IS_WINDOWS:
                subprocess.Popen(["notepad.exe", str(LOG_FILE)])
            else:
                webbrowser.open(LOG_FILE.resolve().as_uri())
        except OSError as exc:
            messagebox.showerror("Błąd", str(exc), parent=self.window)

    def start(self):
        self.start_button.config(state="disabled", text="URUCHAMIAM")
        self.set_status("Przygotowuję VELTRIX Desktop…", "To może potrwać tylko przy pierwszym uruchomieniu.")
        threading.Thread(target=self._prepare_and_run, daemon=True).start()

    def _prepare_and_run(self):
        try:
            with LOG_FILE.open("w", encoding="utf-8") as log:
                log.write("VELTRIX launcher log\n")

                if not VENV_PYTHON.exists():
                    self.set_status("Tworzę środowisko Pythona…", str(ROOT / ".venv"))
                    result = subprocess.run([sys.executable, "-m", "venv", str(ROOT / ".venv")],
                                            cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
                    if result.returncode:
                        raise RuntimeError("Nie udało się utworzyć środowiska .venv.")

                self.set_status("Sprawdzam biblioteki…", "PyQt6 i psutil")
                result = subprocess.run(
                    [str(VENV_PYTHON), "-m", "pip", "install", "--disable-pip-version-check",
                     "-r", str(ROOT / "requirements.txt")],
                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                )
                if result.returncode:
                    raise RuntimeError("Nie udało się zainstalować bibliotek z requirements.txt.")

                self.set_status("Uruchamiam pulpit VELTRIX…", "Okno powinno pojawić się za chwilę.")
                log.write("\n--- VELTRIX Desktop output ---\n")
                log.flush()

                # Launch separately: closing VELTRIX must not be reported as launcher failure.
                process = subprocess.Popen(
                    [str(VENV_PYTHON), "-m", "veltrix.apps.desktop"],
                    cwd=ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )

                # Give Qt time to start. A process that exits immediately usually
                # indicates an import/startup error, not a normal desktop session.
                try:
                    code = process.wait(timeout=2.5)
                except subprocess.TimeoutExpired:
                    self.set_status("Pulpit działa.", "Aby zamknąć VELTRIX, zamknij okno jego aplikacji.")
                    self.window.after(2500, lambda: self.status.config(text="VELTRIX Desktop jest uruchomiony."))
                    self.window.after(0, lambda: self.start_button.config(state="normal", text="START PONOWNIE"))
                    return

                if code != 0:
                    raise RuntimeError(f"VELTRIX zakończył się natychmiast z kodem {code}. Otwórz log, aby zobaczyć szczegóły.")

        except Exception as exc:
            self.window.after(0, lambda error=str(exc): self._show_error(error))
        finally:
            self.window.after(0, lambda: self.start_button.config(state="normal", text="PONÓW START"))

    def _show_error(self, error):
        self.status.config(text="Uruchomienie nie powiodło się.")
        self.progress.config(text=f"Log zapisano: {LOG_FILE}")
        messagebox.showerror("Błąd VELTRIX", f"{error}\n\nLog: {LOG_FILE}", parent=self.window)


if __name__ == "__main__":
    root = tk.Tk()
    Launcher(root)
    root.mainloop()
