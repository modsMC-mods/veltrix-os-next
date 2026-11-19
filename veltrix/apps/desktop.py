"""VELTRIX desktop shell: file manager, terminal, settings, and gaming launch point."""
import os
import platform
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QDir, QProcess, QTimer, Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QFrame, QGridLayout, QHBoxLayout, QInputDialog,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit, QPushButton,
    QStackedWidget, QTreeView, QVBoxLayout, QWidget,
)

# QFileSystemModel belongs to QtWidgets in PyQt6 builds. Import QtGui as a
# compatibility fallback for differently packaged PyQt6 installations.
try:
    from PyQt6.QtWidgets import QFileSystemModel
except ImportError:
    from PyQt6.QtGui import QFileSystemModel

try:
    import psutil
except ImportError:
    psutil = None

HOME = Path.home()
ACCENT = "#a6ff00"
DARK_STYLE = """
QMainWindow, QWidget { background:#101319; color:#f0f3f6; font-family:'Segoe UI',sans-serif; }
QFrame#sidebar { background:#171b22; border-right:1px solid #2a3039; }
QFrame#card { background:#1b2029; border:1px solid #303743; border-radius:12px; }
QLabel#brand { font-size:22px; font-weight:900; }
QLabel#heading { font-size:28px; font-weight:700; }
QLabel#muted { color:#a0a9b5; }
QPushButton { background:#222833; color:#f0f3f6; border:1px solid #343c49; border-radius:8px; padding:9px 13px; }
QPushButton:hover { border-color:#a6ff00; color:#a6ff00; }
QPushButton#primary { background:#a6ff00; color:#11150b; border:0; font-weight:800; }
QPushButton#nav { background:transparent; border:0; padding:12px; color:#c2c8d0; text-align:left; }
QLineEdit, QTreeView, QPlainTextEdit { background:#171b22; color:#f0f3f6; border:1px solid #343c49; border-radius:7px; padding:8px; }
"""
LIGHT_STYLE = """
QMainWindow, QWidget { background:#f3f5f7; color:#20242a; font-family:'Segoe UI',sans-serif; }
QFrame#sidebar { background:#e6e9ed; border-right:1px solid #cbd1d8; }
QFrame#card { background:white; border:1px solid #d8dde3; border-radius:12px; }
QLabel#brand { font-size:22px; font-weight:900; }
QLabel#heading { font-size:28px; font-weight:700; }
QLabel#muted { color:#606b78; }
QPushButton { background:white; color:#20242a; border:1px solid #cbd1d8; border-radius:8px; padding:9px 13px; }
QPushButton:hover { border-color:#6b8e23; color:#496719; }
QPushButton#primary { background:#7cad26; color:white; border:0; font-weight:800; }
QPushButton#nav { background:transparent; border:0; padding:12px; color:#404954; text-align:left; }
QLineEdit, QTreeView, QPlainTextEdit { background:white; color:#20242a; border:1px solid #cbd1d8; border-radius:7px; padding:8px; }
"""


class SystemCard(QFrame):
    def __init__(self, title, value, detail):
        super().__init__()
        self.setObjectName("card")
        box = QVBoxLayout(self)
        box.setContentsMargins(17, 15, 17, 15)
        title_label = QLabel(title.upper())
        title_label.setObjectName("muted")
        self.value = QLabel(value)
        self.value.setStyleSheet("font-size:23px;font-weight:700;")
        self.detail = QLabel(detail)
        self.detail.setObjectName("muted")
        box.addWidget(title_label)
        box.addWidget(self.value)
        box.addWidget(self.detail)


class TerminalPage(QWidget):
    def __init__(self):
        super().__init__()
        self.cwd = HOME
        self.process = None
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("font-family:Consolas,monospace;font-size:13px;padding:12px;")
        self.console.appendPlainText("VELTRIX Terminal — polecenia działają z uprawnieniami bieżącego użytkownika.")
        self.console.appendPlainText(f"Katalog: {self.cwd}")
        self.command = QLineEdit()
        self.command.setPlaceholderText("Wpisz polecenie i naciśnij Enter…")
        self.command.returnPressed.connect(self.run_command)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.addWidget(self.console, 1)
        layout.addWidget(self.command)

    def run_command(self):
        text = self.command.text().strip()
        if not text or self.process is not None:
            return
        self.command.clear()
        self.console.appendPlainText(f"\n{self.cwd} > {text}")
        if text.lower() in ("clear", "cls"):
            self.console.clear()
            return
        if text.lower() in ("exit", "quit"):
            self.console.appendPlainText("Terminal nadal działa. Wpisz polecenie lub zamknij VELTRIX.")
            return
        if text.lower() == "cd" or text.lower().startswith("cd "):
            target = text[2:].strip().strip('"') or str(HOME)
            path = Path(target).expanduser()
            if not path.is_absolute():
                path = self.cwd / path
            if path.is_dir():
                self.cwd = path.resolve()
                self.console.appendPlainText(str(self.cwd))
            else:
                self.console.appendPlainText(f"Folder nie istnieje: {path}")
            return

        process = QProcess(self)
        process.setWorkingDirectory(str(self.cwd))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        if os.name == "nt":
            process.setProgram(os.environ.get("COMSPEC", "cmd.exe"))
            process.setArguments(["/d", "/s", "/c", text])
        else:
            process.setProgram(os.environ.get("SHELL", "/bin/bash"))
            process.setArguments(["-lc", text])
        process.readyReadStandardOutput.connect(lambda p=process: self._read_output(p))
        process.finished.connect(lambda code, status, p=process: self._finished(p, code))
        self.process = process
        self.command.setEnabled(False)
        process.start()

    def _read_output(self, process):
        data = bytes(process.readAllStandardOutput()).decode(errors="replace")
        if data:
            self.console.moveCursor(self.console.textCursor().MoveOperation.End)
            self.console.insertPlainText(data)
            self.console.ensureCursorVisible()

    def _finished(self, process, code):
        self._read_output(process)
        self.console.appendPlainText(f"[zakończono: {code}]")
        self.process = None
        self.command.setEnabled(True)
        self.command.setFocus()


class VeltrixDesktop(QMainWindow):
    PAGES = ["Pulpit", "Pliki", "Terminal", "Gaming", "Ustawienia"]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VELTRIX Desktop")
        self.resize(1360, 850)
        self.setMinimumSize(980, 650)
        self.setStyleSheet(DARK_STYLE)
        self.stack = QStackedWidget()
        self.nav_buttons = []
        self._build_shell()
        self.stack.addWidget(self._home_page())
        self.stack.addWidget(self._files_page())
        self.terminal = TerminalPage()
        self.stack.addWidget(self.terminal)
        self.stack.addWidget(self._gaming_page())
        self.stack.addWidget(self._settings_page())
        self._select_page(0)
        self.clock = QTimer(self)
        self.clock.timeout.connect(self._update_clock)
        self.clock.start(1000)
        self.metrics = QTimer(self)
        self.metrics.timeout.connect(self._refresh_metrics)
        self.metrics.start(2000)
        self._refresh_metrics()
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self._focus_path)
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self._refresh_files)

    def _build_shell(self):
        central = QWidget()
        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        body = QHBoxLayout()
        body.setSpacing(0)

        self.sidebar = QFrame(objectName="sidebar")
        self.sidebar.setFixedWidth(220)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(15, 20, 15, 14)
        brand = QLabel("V<span style='color:#a6ff00'>/</span>ELTRIX")
        brand.setTextFormat(Qt.TextFormat.RichText)
        brand.setObjectName("brand")
        side.addWidget(brand)
        side.addWidget(QLabel("DESKTOP • PLAY • CREATE", objectName="muted"))
        side.addSpacing(24)
        icons = ["⌂", "▤", ">_", "🎮", "⚙"]
        for i, name in enumerate(self.PAGES):
            button = QPushButton(f"{icons[i]}   {name}")
            button.setObjectName("nav")
            button.clicked.connect(lambda checked=False, index=i: self._select_page(index))
            side.addWidget(button)
            self.nav_buttons.append(button)
        side.addStretch()
        side.addWidget(QLabel("LOCAL USER SESSION", objectName="muted"))
        body.addWidget(self.sidebar)
        body.addWidget(self.stack, 1)
        main.addLayout(body, 1)

        taskbar = QFrame(objectName="sidebar")
        taskbar.setFixedHeight(48)
        taskrow = QHBoxLayout(taskbar)
        taskrow.setContentsMargins(16, 3, 18, 3)
        menu = QPushButton("◉  VELTRIX")
        menu.clicked.connect(lambda: self._select_page(0))
        taskrow.addWidget(menu)
        for text, index in (("Pliki", 1), ("Terminal", 2), ("Gaming", 3)):
            button = QPushButton(text)
            button.clicked.connect(lambda checked=False, i=index: self._select_page(i))
            taskrow.addWidget(button)
        taskrow.addStretch()
        self.clock_label = QLabel("")
        taskrow.addWidget(self.clock_label)
        main.addWidget(taskbar)
        self.setCentralWidget(central)

    def _page_header(self, title, description):
        header = QVBoxLayout()
        heading = QLabel(title)
        heading.setObjectName("heading")
        detail = QLabel(description)
        detail.setObjectName("muted")
        detail.setWordWrap(True)
        header.addWidget(heading)
        header.addWidget(detail)
        return header

    def _home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 22)
        layout.setSpacing(18)
        layout.addLayout(self._page_header("Dobry wieczór.", "Pulpit VELTRIX — pliki, terminal, gaming i ustawienia."))
        welcome = QFrame(objectName="card")
        box = QHBoxLayout(welcome)
        box.setContentsMargins(22, 18, 22, 18)
        text = QVBoxLayout()
        text.addWidget(QLabel("VELTRIX DESKTOP", objectName="muted"))
        title = QLabel("Witaj na swoim pulpicie.")
        title.setStyleSheet("font-size:26px;font-weight:700;")
        text.addWidget(title)
        text.addWidget(QLabel("Lekki desktop działający na istniejącym Windows lub Linux.", objectName="muted"))
        box.addLayout(text, 1)
        start = QPushButton("Otwórz Gaming Hub  →")
        start.setObjectName("primary")
        start.clicked.connect(self._launch_gaming_hub)
        box.addWidget(start)
        layout.addWidget(welcome)

        cards = QGridLayout()
        cards.setSpacing(12)
        self.cpu_card = SystemCard("Procesor", "—", "Bieżące użycie")
        self.memory_card = SystemCard("Pamięć RAM", "—", "Bieżące użycie")
        self.platform_card = SystemCard("System hosta", platform.system(), platform.release())
        for i, card in enumerate((self.cpu_card, self.memory_card, self.platform_card)):
            cards.addWidget(card, 0, i)
        layout.addLayout(cards)

        layout.addWidget(QLabel("SZYBKIE URUCHAMIANIE", objectName="muted"))
        shortcuts = QGridLayout()
        defs = [("▤  Menedżer plików", 1), (">_  Terminal", 2),
                ("🎮  Gaming Hub", 3), ("⌂  Pulpit", 0)]
        for i, (name, page_index) in enumerate(defs):
            button = QPushButton(name)
            button.setMinimumHeight(64)
            button.clicked.connect(lambda checked=False, p=page_index: self._select_page(p))
            shortcuts.addWidget(button, i // 2, i % 2)
        layout.addLayout(shortcuts)
        layout.addStretch()
        return page

    def _files_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(25, 22, 25, 20)
        layout.addLayout(self._page_header("Menedżer plików", "Przeglądaj i otwieraj pliki, do których ma dostęp bieżący użytkownik."))
        bar = QHBoxLayout()
        home = QPushButton("⌂  Dom")
        home.clicked.connect(lambda: self._navigate_files(str(HOME)))
        up = QPushButton("↑  W górę")
        up.clicked.connect(self._parent_folder)
        self.path_edit = QLineEdit(str(HOME))
        self.path_edit.returnPressed.connect(lambda: self._navigate_files(self.path_edit.text()))
        go = QPushButton("Idź")
        go.clicked.connect(lambda: self._navigate_files(self.path_edit.text()))
        new_folder = QPushButton("＋ Folder")
        new_folder.clicked.connect(self._new_folder)
        open_item = QPushButton("Otwórz")
        open_item.clicked.connect(self._open_selected_file)
        for widget in (home, up, self.path_edit, go, new_folder, open_item):
            bar.addWidget(widget)
        layout.addLayout(bar)

        self.fs_model = QFileSystemModel(self)
        self.fs_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | QDir.Filter.Drives)
        self.fs_model.setRootPath(str(HOME))
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.fs_model)
        self.file_tree.setRootIndex(self.fs_model.index(str(HOME)))
        self.file_tree.setColumnWidth(0, 450)
        self.file_tree.doubleClicked.connect(self._tree_double_click)
        layout.addWidget(self.file_tree, 1)
        tip = QLabel("Ctrl+L: ścieżka  •  Ctrl+R: odśwież  •  dwuklik otwiera folder lub plik")
        tip.setObjectName("muted")
        layout.addWidget(tip)
        return page

    def _gaming_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 20)
        layout.addLayout(self._page_header("Gaming", "Gaming Hub dla biblioteki, wydajności i narzędzi Linux."))
        card = QFrame(objectName="card")
        box = QVBoxLayout(card)
        box.setContentsMargins(20, 18, 20, 18)
        box.addWidget(QLabel("Otwórz pełny gamingowy dashboard VELTRIX PLAY."))
        button = QPushButton("▶  Uruchom Gaming Hub")
        button.setObjectName("primary")
        button.clicked.connect(self._launch_gaming_hub)
        box.addWidget(button)
        layout.addWidget(card)
        for text in ("Biblioteka i wykrywanie lokalnego Steam",
                     "Uruchamianie gier przez Steam lub plik wykonywalny",
                     "Podgląd CPU i RAM",
                     "Wykrywanie Steam, GameMode i MangoHud"):
            layout.addWidget(QLabel("•  " + text, objectName="muted"))
        layout.addStretch()
        return page

    def _settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 25, 30, 20)
        layout.addLayout(self._page_header("Ustawienia", "Personalizacja sesji VELTRIX."))
        card = QFrame(objectName="card")
        box = QVBoxLayout(card)
        box.setContentsMargins(20, 18, 20, 18)
        box.addWidget(QLabel("Wygląd"))
        theme = QCheckBox("Jasny motyw")
        theme.stateChanged.connect(self._toggle_theme)
        box.addWidget(theme)
        box.addWidget(QLabel("VELTRIX działa jako aplikacja użytkownika i nie zmienia sterowników, partycji ani ekranu logowania.", objectName="muted"))
        layout.addWidget(card)
        layout.addStretch()
        return page

    def _select_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setStyleSheet("color:#a6ff00;" if i == index else "")

    def _toggle_theme(self, state):
        self.setStyleSheet(LIGHT_STYLE if state else DARK_STYLE)

    def _refresh_metrics(self):
        if psutil is not None:
            self.cpu_card.value.setText(f"{psutil.cpu_percent():.0f}%")
            ram = psutil.virtual_memory()
            self.memory_card.value.setText(f"{ram.percent:.0f}%")
            self.memory_card.detail.setText(f"{ram.used / 1024**3:.1f} / {ram.total / 1024**3:.1f} GB")

    def _update_clock(self):
        self.clock_label.setText(datetime.now().strftime("%a  %d %b  •  %H:%M"))

    def _navigate_files(self, raw_path):
        path = Path(raw_path).expanduser()
        if not path.exists() or not path.is_dir():
            QMessageBox.warning(self, "Nie można otworzyć folderu", f"Folder nie istnieje lub nie jest dostępny:\n{path}")
            return
        resolved = str(path.resolve())
        self.path_edit.setText(resolved)
        self.file_tree.setRootIndex(self.fs_model.index(resolved))

    def _parent_folder(self):
        self._navigate_files(str(Path(self.path_edit.text()).parent))

    def _refresh_files(self):
        self._navigate_files(self.path_edit.text())

    def _focus_path(self):
        if self.stack.currentIndex() == 1:
            self.path_edit.setFocus()
            self.path_edit.selectAll()

    def _tree_double_click(self, index):
        path = Path(self.fs_model.filePath(index))
        if path.is_dir():
            self._navigate_files(str(path))
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _open_selected_file(self):
        index = self.file_tree.currentIndex()
        if index.isValid():
            self._tree_double_click(index)

    def _new_folder(self):
        name, ok = QInputDialog.getText(self, "Nowy folder", "Nazwa folderu:")
        if not ok or not name.strip():
            return
        target = Path(self.path_edit.text()) / name.strip()
        try:
            target.mkdir()
            self._refresh_files()
        except OSError as error:
            QMessageBox.critical(self, "Nie można utworzyć folderu", str(error))

    def _launch_gaming_hub(self):
        try:
            subprocess.Popen([sys.executable, "-m", "veltrix"], cwd=Path(__file__).resolve().parents[2])
        except OSError as error:
            QMessageBox.critical(self, "Nie można uruchomić Gaming Hub", str(error))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VELTRIX Desktop")
    window = VeltrixDesktop()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        log = Path.home() / "veltrix-desktop-startup.log"
        log.write_text(traceback.format_exc(), encoding="utf-8")
        raise
