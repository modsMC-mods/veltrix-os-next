"""Polished VELTRIX shell with an Applications menu and extra utilities."""
import os
import platform
import shutil
import socket
import time
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QDesktopServices, QUrl
from PyQt6.QtWidgets import QApplication, QMessageBox

from veltrix.apps.desktop import Desktop, Terminal as BaseTerminal
from veltrix.apps.toolbox import Calculator, Notes, ProcessManager, safe_calculate, save_screenshot


class BetterTerminal(BaseTerminal):
    def builtin(self, raw):
        parts = raw[1:].split(maxsplit=1)
        command = parts[0].casefold() if parts else "help"
        argument = parts[1] if len(parts) > 1 else ""
        if command in ("help", "?"):
            super().builtin(raw)
            self.output.appendPlainText("""
Dodatkowe komendy VELTRIX:
/calc <działanie>     bezpieczny kalkulator, np. /calc (2+3)*4
/note [tekst]         otwórz lokalne Notes; opcjonalny tekst wstaw do notatki
/clipboard            pokaż zawartość schowka systemowego
/uptime               czas od uruchomienia komputera
/battery              stan baterii (jeśli dostępna)
/processes            podgląd 100 procesów o największym użyciu CPU
/screenshot           zapisz zrzut głównego ekranu jako PNG
/network              pokaż liczniki ruchu sieciowego
/which <program>      znajdź program w PATH
/free                 wolne miejsce na dysku bieżącego katalogu
""")
            return
        try:
            if command == "calc":
                if not argument.strip():
                    raise ValueError("Użycie: /calc <działanie>")
                self.output.appendPlainText("= " + safe_calculate(argument))
            elif command == "note":
                self.parent().show_tool(Notes, initial_text=argument)
            elif command == "clipboard":
                value = QApplication.clipboard().text()
                self.output.appendPlainText(value if value else "Schowek tekstowy jest pusty.")
            elif command == "uptime":
                if not _psutil():
                    raise RuntimeError("Komenda wymaga pakietu psutil.")
                self.output.appendPlainText(f"System działa od {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(_psutil().boot_time()))}")
            elif command == "battery":
                battery = _psutil().sensors_battery() if _psutil() else None
                self.output.appendPlainText("Brak wykrytej baterii." if battery is None else f"Bateria: {battery.percent:.0f}% • {'ładowanie' if battery.power_plugged else 'zasilanie bateryjne'}")
            elif command == "processes":
                self.parent().show_tool(ProcessManager)
            elif command == "screenshot":
                path = save_screenshot(self)
                if path:
                    self.output.appendPlainText(f"Zapisano: {path}")
            elif command == "network":
                p = _psutil()
                if not p:
                    raise RuntimeError("Komenda wymaga psutil.")
                stats = p.net_io_counters()
                self.output.appendPlainText(f"Wysłano: {stats.bytes_sent / 1024**2:.1f} MB • Odebrano: {stats.bytes_recv / 1024**2:.1f} MB")
            elif command == "which":
                if not argument.strip():
                    raise ValueError("Użycie: /which <program>")
                self.output.appendPlainText(shutil.which(argument.strip()) or "Nie znaleziono w PATH.")
            elif command == "free":
                usage = shutil.disk_usage(str(self.cwd))
                self.output.appendPlainText(f"Wolne: {usage.free / 1024**3:.1f} GB • Łącznie: {usage.total / 1024**3:.1f} GB")
            else:
                return super().builtin(raw)
        except Exception as error:
            self.output.appendPlainText(f"Błąd: {error}")


def _psutil():
    try:
        import psutil
        return psutil
    except ImportError:
        return None


class VELTRIX(Desktop):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VELTRIX Desktop • Essentials")
        self.install_apps_menu()

    def install_apps_menu(self):
        bar = self.menuBar()
        apps = bar.addMenu("Aplikacje")
        entries = (
            ("🌐  Przeglądarka", lambda: self.open_browser()),
            ("📁  Eksplorator plików", lambda: self.open_explorer()),
            (">_  Terminal • /help", self.open_terminal),
            ("📝  Notes", lambda: self.show_tool(Notes)),
            ("🧮  Kalkulator", lambda: self.show_tool(Calculator)),
            ("📊  Menedżer procesów", lambda: self.show_tool(ProcessManager)),
            ("📸  Zrzut ekranu", self.take_screenshot),
            ("🎮  Gaming Hub", self.open_gaming),
        )
        for label, callback in entries:
            action = QAction(label, self)
            action.triggered.connect(callback)
            apps.addAction(action)
        system = bar.addMenu("System")
        info = QAction("Informacje o komputerze", self)
        info.triggered.connect(self.show_system)
        system.addAction(info)
        theme = QAction("Przełącz jasny/ciemny motyw", self)
        theme.triggered.connect(lambda: self.set_theme(not self.light))
        system.addAction(theme)
        help_menu = bar.addMenu("Pomoc")
        help_action = QAction("50 pomysłów na rozwój", self)
        help_action.triggered.connect(self.show_roadmap)
        help_menu.addAction(help_action)

    def show_tool(self, window_type, initial_text=""):
        if window_type is Notes:
            window = Notes(self, initial_text=initial_text)
        else:
            window = window_type(self)
        self.show_window(window)
        return window

    def open_terminal(self):
        window = BetterTerminal(self, self.open_browser, self.open_explorer, self.set_theme)
        self.show_window(window)

    def take_screenshot(self):
        path = save_screenshot(self)
        if path:
            QMessageBox.information(self, "Zrzut zapisany", f"Zapisano obraz:\n{path}")

    def show_roadmap(self):
        path = Path(__file__).resolve().parents[2] / "FEATURE-ROADMAP-50.md"
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        else:
            QMessageBox.information(self, "Roadmap", "Zobacz FEATURE-ROADMAP-50.md w folderze projektu.")


def main():
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("VELTRIX Desktop")
    app.setStyle("Fusion")
    window = VELTRIX()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
