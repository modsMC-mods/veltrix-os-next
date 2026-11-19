"""VELTRIX OS Next desktop entry point."""
import importlib
import logging
import os
import sys
import traceback
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QLabel, QMainWindow, QMessageBox,
    QPushButton, QVBoxLayout, QWidget,
)

APP_TITLE = "VELTRIX OS Next"
LOG_DIR = Path.home() / ".local" / "state" / "veltrix-os"
LOG_FILE = LOG_DIR / "startup.log"
APPS = {
    "Centrum sterowania": ("veltrix.apps.control_center", "ControlCenter"),
    "Logowanie": ("veltrix.apps.login", "Login"),
    "Wyszukiwanie": ("veltrix.apps.search", "Search"),
    "Zrzuty ekranu": ("veltrix.apps.screenshots", "Screenshots"),
    "Nagrywanie ekranu": ("veltrix.apps.recorder", "Recorder"),
    "Odtwarzacz multimediów": ("veltrix.apps.media", "MediaPlayer"),
    "Przeglądarka obrazów": ("veltrix.apps.images", "ImageViewer"),
    "Menedżer pakietów": ("veltrix.apps.packages", "PackageManager"),
    "Aktualizator": ("veltrix.apps.updater", "Updater"),
    "Kreator pierwszego uruchomienia": ("veltrix.apps.wizard", "FirstRunWizard"),
    "Sieć": ("veltrix.apps.network", "Network"),
    "Bluetooth": ("veltrix.apps.bluetooth", "Bluetooth"),
    "Dźwięk": ("veltrix.apps.audio", "Audio"),
    "Raport błędu": ("veltrix.apps.bugreport", "BugReport"),
}


def log_exception(exc_type, exc_value, exc_tb):
    """Keep startup/runtime tracebacks available after a console closes."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as log:
            traceback.print_exception(exc_type, exc_value, exc_tb, file=log)
            log.write("\n")
    except OSError:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)


class Desktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 720)
        self.setMinimumSize(720, 480)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #0b1020; color: #edf3ff; font-family: sans-serif; }
            QFrame#header { background: #11182a; border-radius: 14px; }
            QPushButton { background: #172039; color: #edf3ff; border: 1px solid #293657;
                          border-radius: 10px; padding: 14px; text-align: left; }
            QPushButton:hover { background: #315eea; }
            QLabel#muted { color: #9ba9c7; }
        """)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        header = QFrame(objectName="header")
        header_layout = QVBoxLayout(header)
        title = QLabel("VELTRIX OS")
        title.setStyleSheet("font-size: 30px; font-weight: 700; color: #69a5ff;")
        subtitle = QLabel("Twoje środowisko Linux • Python + PyQt6")
        subtitle.setObjectName("muted")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)

        layout.addWidget(QLabel("Aplikacje"))
        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(12)
        self.windows = []
        for index, (name, spec) in enumerate(APPS.items()):
            button = QPushButton(name)
            button.setMinimumHeight(58)
            button.clicked.connect(lambda checked=False, n=name, s=spec: self.open_app(n, s))
            grid.addWidget(button, index // 3, index % 3)
        layout.addWidget(grid_host)
        layout.addStretch(1)

        note = QLabel("VELTRIX jest aplikacją desktopową działającą na istniejącym systemie; nie zastępuje kernela Linux.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.setCentralWidget(root)

    def open_app(self, title, spec):
        try:
            module = importlib.import_module(spec[0])
            widget_class = getattr(module, spec[1])
            widget = widget_class()
            widget.setWindowTitle(title)
            widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
            self.windows.append(widget)
            widget.destroyed.connect(lambda: self.windows.remove(widget) if widget in self.windows else None)
            widget.show()
        except Exception as error:
            log_exception(type(error), error, error.__traceback__)
            QMessageBox.critical(
                self, f"Nie można uruchomić: {title}",
                f"Aplikacja nie wystartowała.\n\n{error}\n\nSzczegóły zapisano w:\n{LOG_FILE}",
            )


def main():
    sys.excepthook = log_exception
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    window = Desktop()
    window.showMaximized() if os.environ.get("VELTRIX_MAXIMIZED") == "1" else window.show()
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        log_exception(type(error), error, error.__traceback__)
        raise
