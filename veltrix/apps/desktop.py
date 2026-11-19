"""VELTRIX Desktop: Windows-inspired user-space desktop for Windows/Linux."""
import os
import platform
import shutil
import socket
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QProcess, QTimer, Qt, QUrl
from PyQt6.QtGui import QAction, QColor, QDesktopServices, QKeySequence, QLinearGradient, QPainter, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QInputDialog, QLabel, QLineEdit, QMainWindow, QMenu,
    QMessageBox, QPlainTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QVBoxLayout, QWidget,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

try:
    import psutil
except ImportError:
    psutil = None

ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
DARK = """
QMainWindow,QWidget {background:#10141c;color:#f4f6fb;font-family:'Segoe UI',sans-serif;}
QFrame#taskbar,QFrame#glass,QFrame#panel {background:#171d29;border:1px solid #30394a;border-radius:14px;}
QLabel#muted {color:#aab4c5;} QLabel#heading {font-size:25px;font-weight:700;}
QPushButton {background:#222a38;color:#f4f6fb;border:1px solid #394457;border-radius:9px;padding:9px 13px;}
QPushButton:hover {background:#303b4e;border-color:#a6ff00;}
QPushButton#primary {background:#a6ff00;color:#11150b;border:0;font-weight:800;}
QPushButton#desktopIcon {background:transparent;border:1px solid transparent;padding:10px;}
QPushButton#desktopIcon:hover {background:rgba(255,255,255,35);border-color:rgba(255,255,255,65);}
QLineEdit,QTableWidget,QPlainTextEdit {background:#121720;color:#f4f6fb;border:1px solid #394457;border-radius:8px;padding:8px;selection-background-color:#47651a;}
QTableWidget {gridline-color:#283140;} QHeaderView::section {background:#1b2330;color:#b8c2d2;border:0;padding:8px;}
QMenu {background:#171d29;color:#f4f6fb;border:1px solid #394457;padding:8px;} QMenu::item {padding:9px 24px;} QMenu::item:selected {background:#303b4e;color:#a6ff00;}
QTabWidget::pane {border:1px solid #394457;border-radius:8px;} QTabBar::tab {background:#202735;color:#e7edf5;padding:9px 14px;border-radius:6px;}
"""
LIGHT = """
QMainWindow,QWidget {background:#f0f3f8;color:#202938;font-family:'Segoe UI',sans-serif;}
QFrame#taskbar,QFrame#glass,QFrame#panel {background:#f8faff;border:1px solid #d5dce7;border-radius:14px;}
QLabel#muted {color:#647187;} QLabel#heading {font-size:25px;font-weight:700;}
QPushButton {background:#e9eef6;color:#202938;border:1px solid #d0d8e5;border-radius:9px;padding:9px 13px;}
QPushButton:hover {background:#dfe8f5;border-color:#709326;} QPushButton#primary {background:#7cac20;color:white;border:0;font-weight:800;}
QPushButton#desktopIcon {background:transparent;border:1px solid transparent;padding:10px;} QLineEdit,QTableWidget,QPlainTextEdit {background:white;color:#202938;border:1px solid #d0d8e5;border-radius:8px;padding:8px;}
QHeaderView::section {background:#e7edf5;color:#435066;border:0;padding:8px;} QMenu {background:#f8faff;color:#202938;border:1px solid #d0d8e5;padding:8px;}
QMenu::item {padding:9px 24px;} QMenu::item:selected {background:#e3ebd7;color:#496719;}
QTabWidget::pane {border:1px solid #d0d8e5;} QTabBar::tab {background:#e9eef6;color:#202938;padding:9px 14px;}
"""


def as_url(text):
    text = text.strip()
    if not text:
        return QUrl("https://duckduckgo.com")
    if " " in text or ("." not in text and not text.startswith(("http://", "https://", "file:"))):
        return QUrl("https://duckduckgo.com/?q=" + QUrl.toPercentEncoding(text).data().decode())
    if "://" not in text and not text.startswith("file:"):
        text = "https://" + text
    return QUrl.fromUserInput(text)


class Browser(QMainWindow):
    """Tabbed Chromium-based browser window using Qt WebEngine."""
    def __init__(self, parent=None, initial_url="https://duckduckgo.com"):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("VELTRIX Browser")
        self.resize(1120, 740)
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        bar = QHBoxLayout()
        for label, slot in (("←", self.back), ("→", self.forward), ("⟳", self.reload), ("⌂", self.home)):
            button = QPushButton(label)
            button.setFixedWidth(42)
            button.clicked.connect(slot)
            bar.addWidget(button)
        self.address = QLineEdit()
        self.address.setPlaceholderText("Wpisz adres lub szukaj w sieci…")
        self.address.returnPressed.connect(self.navigate)
        bar.addWidget(self.address, 1)
        add = QPushButton("＋ Karta")
        add.clicked.connect(lambda: self.add_tab())
        bar.addWidget(add)
        layout.addLayout(bar)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.sync_address)
        layout.addWidget(self.tabs, 1)
        self.setCentralWidget(central)
        self.add_tab(initial_url)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.focus_address)
        QShortcut(QKeySequence("Ctrl+T"), self, activated=lambda: self.add_tab())
        QShortcut(QKeySequence("Ctrl+W"), self, activated=lambda: self.close_tab(self.tabs.currentIndex()))

    def add_tab(self, url="https://duckduckgo.com"):
        view = QWebEngineView()
        index = self.tabs.addTab(view, "Nowa karta")
        self.tabs.setCurrentIndex(index)
        view.urlChanged.connect(lambda value, v=view: self.address.setText(value.toString()) if v is self.current_view() else None)
        view.titleChanged.connect(lambda title, v=view: self.set_tab_title(v, title))
        view.load(as_url(url))
        return view

    def current_view(self):
        return self.tabs.currentWidget()

    def set_tab_title(self, view, title):
        index = self.tabs.indexOf(view)
        if index >= 0:
            self.tabs.setTabText(index, (title or "Karta")[:24])
            if view is self.current_view():
                self.setWindowTitle((title or "VELTRIX Browser") + " — VELTRIX")

    def navigate(self):
        view = self.current_view()
        if view:
            view.load(as_url(self.address.text()))

    def back(self):
        if self.current_view(): self.current_view().back()

    def forward(self):
        if self.current_view(): self.current_view().forward()

    def reload(self):
        if self.current_view(): self.current_view().reload()

    def home(self):
        if self.current_view(): self.current_view().load(QUrl("https://duckduckgo.com"))

    def focus_address(self):
        self.address.setFocus()
        self.address.selectAll()

    def sync_address(self, index):
        view = self.current_view()
        if view:
            self.address.setText(view.url().toString())
            self.setWindowTitle(view.title() + " — VELTRIX" if view.title() else "VELTRIX Browser")

    def close_tab(self, index):
        if self.tabs.count() <= 1:
            self.close()
        else:
            self.tabs.widget(index).deleteLater()
            self.tabs.removeTab(index)


class Explorer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("VELTRIX Explorer")
        self.resize(950, 620)
        self.path = HOME
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 14, 16, 16)
        title = QLabel("Eksplorator plików")
        title.setObjectName("heading")
        layout.addWidget(title)
        bar = QHBoxLayout()
        for label, action in (("← Wstecz", self.go_up), ("⌂ Dom", self.go_home), ("Odśwież", self.refresh)):
            btn = QPushButton(label)
            btn.clicked.connect(action)
            bar.addWidget(btn)
        self.address = QLineEdit(str(HOME))
        self.address.returnPressed.connect(lambda: self.navigate(self.address.text()))
        bar.addWidget(self.address, 1)
        go = QPushButton("Idź")
        go.clicked.connect(lambda: self.navigate(self.address.text()))
        bar.addWidget(go)
        layout.addLayout(bar)
        tools = QHBoxLayout()
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("Filtruj widoczne pliki…")
        self.filter.textChanged.connect(self.filter_rows)
        tools.addWidget(self.filter, 1)
        for label, action in (("＋ Folder", self.new_folder), ("＋ Plik", self.new_file), ("Otwórz", self.open_selected)):
            btn = QPushButton(label)
            btn.clicked.connect(action)
            tools.addWidget(btn)
        layout.addLayout(tools)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nazwa", "Typ", "Rozmiar", "Zmodyfikowano"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in (1, 2, 3): self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellDoubleClicked.connect(self.open_row)
        layout.addWidget(self.table, 1)
        self.status = QLabel("")
        self.status.setObjectName("muted")
        layout.addWidget(self.status)
        self.setCentralWidget(central)
        self.navigate(str(HOME))
        QShortcut(QKeySequence("Alt+Up"), self, activated=self.go_up)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=lambda: (self.address.setFocus(), self.address.selectAll()))
        QShortcut(QKeySequence("F5"), self, activated=self.refresh)

    def navigate(self, value):
        path = Path(value).expanduser()
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold()))
            self.path = path.resolve()
            self.address.setText(str(self.path))
            self.table.setRowCount(0)
            for entry in entries:
                try:
                    stat = entry.stat()
                    kind = "Folder" if entry.is_dir() else (entry.suffix[1:].upper() or "Plik")
                    size = "—" if entry.is_dir() else self.size(stat.st_size)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                except OSError:
                    kind, size, modified = "Niedostępny", "—", "—"
                row = self.table.rowCount()
                self.table.insertRow(row)
                name_item = QTableWidgetItem(("📁  " if entry.is_dir() else "📄  ") + entry.name)
                name_item.setData(Qt.ItemDataRole.UserRole, str(entry))
                self.table.setItem(row, 0, name_item)
                for col, value in enumerate((kind, size, modified), 1): self.table.setItem(row, col, QTableWidgetItem(value))
            self.status.setText(f"{len(entries)} elementów • {self.path}")
        except OSError as error:
            QMessageBox.warning(self, "Nie można otworzyć folderu", f"{path}\n\n{error}")

    @staticmethod
    def size(n):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024 or unit == "TB": return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
            n /= 1024

    def filter_rows(self, text):
        q = text.casefold()
        for row in range(self.table.rowCount()): self.table.setRowHidden(row, bool(q) and q not in self.table.item(row, 0).text().casefold())

    def go_home(self): self.navigate(str(HOME))
    def go_up(self):
        if self.path.parent != self.path: self.navigate(str(self.path.parent))
    def refresh(self): self.navigate(str(self.path))

    def selected_path(self):
        row = self.table.currentRow()
        item = self.table.item(row, 0) if row >= 0 else None
        return Path(item.data(Qt.ItemDataRole.UserRole)) if item else None

    def open_selected(self):
        path = self.selected_path()
        if path: self.open_path(path)

    def open_row(self, row, column):
        item = self.table.item(row, 0)
        if item: self.open_path(Path(item.data(Qt.ItemDataRole.UserRole)))

    def open_path(self, path):
        if path.is_dir(): self.navigate(str(path))
        else: QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def new_folder(self):
        name, ok = QInputDialog.getText(self, "Nowy folder", "Nazwa folderu:")
        if ok and name.strip():
            try: (self.path / name.strip()).mkdir(); self.refresh()
            except OSError as e: QMessageBox.critical(self, "Błąd", str(e))

    def new_file(self):
        name, ok = QInputDialog.getText(self, "Nowy plik", "Nazwa pliku:")
        if ok and name.strip():
            try: (self.path / name.strip()).touch(exist_ok=False); self.refresh()
            except OSError as e: QMessageBox.critical(self, "Błąd", str(e))


class Terminal(QMainWindow):
    """Shell with a useful built-in slash command set plus normal host commands."""
    def __init__(self, parent=None, open_browser=None, open_explorer=None, set_theme=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("VELTRIX Terminal")
        self.resize(850, 560)
        self.cwd = HOME
        self.process = None
        self.open_browser_cb = open_browser
        self.open_explorer_cb = open_explorer
        self.set_theme_cb = set_theme
        center = QWidget()
        layout = QVBoxLayout(center)
        layout.setContentsMargins(16, 16, 16, 16)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("font-family:Consolas,monospace;font-size:13px;")
        self.output.appendPlainText("VELTRIX Terminal • wpisz /help, aby zobaczyć wbudowane komendy.")
        self.output.appendPlainText(f"Katalog: {self.cwd}")
        self.input = QLineEdit()
        self.input.setPlaceholderText("/help — pomoc • zwykłe polecenia hosta też działają")
        self.input.returnPressed.connect(self.run_command)
        layout.addWidget(self.output, 1)
        layout.addWidget(self.input)
        self.setCentralWidget(center)
        self.history = []
        self.history_index = 0
        self.input.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up and self.history:
                self.history_index = max(0, self.history_index - 1)
                self.input.setText(self.history[self.history_index])
                return True
            if event.key() == Qt.Key.Key_Down and self.history:
                self.history_index = min(len(self.history), self.history_index + 1)
                self.input.setText(self.history[self.history_index] if self.history_index < len(self.history) else "")
                return True
        return super().eventFilter(obj, event)

    def run_command(self):
        text = self.input.text().strip()
        if not text or self.process: return
        self.input.clear()
        self.history.append(text)
        self.history_index = len(self.history)
        self.output.appendPlainText(f"\n{self.cwd} > {text}")
        if text.startswith("/"):
            self.builtin(text)
            return
        if text.casefold() in ("clear", "cls"):
            self.output.clear()
            return
        self.run_host_command(text)

    def builtin(self, raw):
        parts = raw[1:].split(maxsplit=1)
        cmd = parts[0].casefold() if parts else "help"
        arg = parts[1].strip().strip('"') if len(parts) > 1 else ""
        try:
            if cmd in ("help", "?"):
                self.output.appendPlainText("""VELTRIX built-ins (use /command [argument]):
/help, /clear                 pomoc i wyczyszczenie ekranu
/pwd, /ls [folder]            bieżący katalog i lista plików
/cd [folder]                  zmień katalog roboczy
/open <ścieżka>               otwórz plik/folder aplikacją hosta
/explorer [folder]            otwórz Eksplorator VELTRIX
/browser [adres lub szukaj]   otwórz wbudowaną przeglądarkę
/date, /time, /whoami          data, godzina i konto użytkownika
/system, /cpu, /ram, /disk     informacje o systemie i zasobach
/ip                           lokalne adresy IP interfejsów
/find <nazwa> [folder]        znajdź nazwę w folderze (maks. 5000 wyników)
/mkdir <nazwa>                utwórz folder w bieżącym katalogu
/touch <nazwa>                utwórz pusty plik
/theme dark|light             zmień motyw VELTRIX
/apps                         skróty dostępne w VELTRIX

Pozostałe polecenia są przekazywane do powłoki Windows/Linux jako bieżący użytkownik.""")
            elif cmd == "clear": self.output.clear()
            elif cmd == "pwd": self.output.appendPlainText(str(self.cwd))
            elif cmd == "ls":
                path = (self.cwd / arg).expanduser() if arg and not Path(arg).is_absolute() else Path(arg).expanduser() if arg else self.cwd
                for item in sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold())):
                    self.output.appendPlainText(("[DIR]  " if item.is_dir() else "       ") + item.name)
            elif cmd == "cd":
                path = Path(arg).expanduser() if arg else HOME
                if not path.is_absolute(): path = self.cwd / path
                if path.is_dir(): self.cwd = path.resolve(); self.output.appendPlainText(str(self.cwd))
                else: self.output.appendPlainText(f"Brak folderu: {path}")
            elif cmd == "open":
                if not arg: raise ValueError("Użycie: /open <ścieżka>")
                path = Path(arg).expanduser()
                if not path.is_absolute(): path = self.cwd / path
                if not path.exists(): raise FileNotFoundError(path)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.resolve())))
            elif cmd == "explorer":
                if self.open_explorer_cb: self.open_explorer_cb(arg)
                else: QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(arg).expanduser() if arg else HOME)))
            elif cmd == "browser":
                if self.open_browser_cb: self.open_browser_cb(arg)
                else: self.output.appendPlainText("Przeglądarka niedostępna.")
            elif cmd == "date": self.output.appendPlainText(datetime.now().strftime("%A, %d %B %Y"))
            elif cmd == "time": self.output.appendPlainText(datetime.now().strftime("%H:%M:%S"))
            elif cmd == "whoami": self.output.appendPlainText(os.environ.get("USERNAME") or os.environ.get("USER") or "unknown")
            elif cmd == "system": self.output.appendPlainText(f"{platform.platform()}\nPython {platform.python_version()}\nHost: {socket.gethostname()}")
            elif cmd == "cpu": self.output.appendPlainText(f"CPU cores: {os.cpu_count() or '?'}\nLoad: {psutil.cpu_percent(interval=.2):.0f}%" if psutil else f"CPU cores: {os.cpu_count() or '?'} (install psutil for usage)")
            elif cmd == "ram":
                if psutil:
                    m = psutil.virtual_memory(); self.output.appendPlainText(f"RAM: {m.percent:.0f}% used • {m.used / 1024**3:.1f}/{m.total / 1024**3:.1f} GB")
                else: self.output.appendPlainText("Zainstaluj psutil, aby odczytać RAM.")
            elif cmd == "disk":
                disks = ["C:\\" if os.name == "nt" else "/"]
                for disk in disks:
                    u = shutil.disk_usage(disk); self.output.appendPlainText(f"{disk} free {u.free / 1024**3:.1f} GB / {u.total / 1024**3:.1f} GB")
            elif cmd == "ip":
                if psutil:
                    for nic, addresses in psutil.net_if_addrs().items():
                        ips = [a.address for a in addresses if a.family in (socket.AF_INET, socket.AF_INET6)]
                        if ips: self.output.appendPlainText(f"{nic}: {', '.join(ips)}")
                else: self.output.appendPlainText(f"Hostname: {socket.gethostname()} • install psutil for interface addresses")
            elif cmd == "find":
                if not arg: raise ValueError("Użycie: /find <nazwa> [folder]")
                tokens = arg.split(maxsplit=1); needle = tokens[0].casefold()
                base = Path(tokens[1]).expanduser() if len(tokens) > 1 else self.cwd
                if not base.is_absolute(): base = self.cwd / base
                count = 0
                for path in base.rglob("*"):
                    if needle in path.name.casefold():
                        self.output.appendPlainText(str(path)); count += 1
                        if count >= 5000: self.output.appendPlainText("Ograniczono do 5000 wyników."); break
                if not count: self.output.appendPlainText("Brak wyników.")
            elif cmd == "mkdir":
                if not arg: raise ValueError("Użycie: /mkdir <nazwa>")
                (self.cwd / arg).mkdir(parents=True, exist_ok=False); self.output.appendPlainText("Folder utworzony.")
            elif cmd == "touch":
                if not arg: raise ValueError("Użycie: /touch <nazwa>")
                (self.cwd / arg).touch(exist_ok=False); self.output.appendPlainText("Plik utworzony.")
            elif cmd == "theme":
                if arg not in ("dark", "light"): raise ValueError("Użycie: /theme dark|light")
                if self.set_theme_cb: self.set_theme_cb(arg == "light")
                self.output.appendPlainText(f"Motyw: {arg}")
            elif cmd == "apps": self.output.appendPlainText("explorer • browser • terminal • gaming • settings")
            else: self.output.appendPlainText(f"Nieznana komenda /{cmd}. Wpisz /help.")
        except Exception as error:
            self.output.appendPlainText(f"Błąd: {error}")

    def run_host_command(self, command):
        process = QProcess(self)
        process.setWorkingDirectory(str(self.cwd))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        if os.name == "nt":
            process.setProgram(os.environ.get("COMSPEC", "cmd.exe")); process.setArguments(["/d", "/s", "/c", command])
        else:
            process.setProgram(os.environ.get("SHELL", "/bin/bash")); process.setArguments(["-lc", command])
        process.readyReadStandardOutput.connect(lambda p=process: self.read_output(p))
        process.finished.connect(lambda code, status, p=process: self.finished(p, code))
        self.process = process; self.input.setEnabled(False); process.start()

    def read_output(self, process):
        text = bytes(process.readAllStandardOutput()).decode(errors="replace")
        if text:
            self.output.moveCursor(self.output.textCursor().MoveOperation.End)
            self.output.insertPlainText(text); self.output.ensureCursorVisible()

    def finished(self, process, code):
        self.read_output(process); self.output.appendPlainText(f"[zakończono: {code}]")
        self.process = None; self.input.setEnabled(True); self.input.setFocus(); process.deleteLater()


class Wallpaper(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#142a3e")); gradient.setColorAt(.5, QColor("#273752")); gradient.setColorAt(1, QColor("#472b4b"))
        painter.fillRect(self.rect(), gradient); painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(48, 187, 176, 75)); painter.drawEllipse(int(self.width()*.56), -180, 680, 680)
        painter.setBrush(QColor(172, 255, 0, 25)); painter.drawEllipse(int(self.width()*.67), int(self.height()*.43), 520, 520)


class Desktop(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("VELTRIX Desktop"); self.resize(1440, 900); self.setMinimumSize(980, 650)
        self.setStyleSheet(DARK); self.light = False; self.windows = []; self.canvas = Wallpaper(); self.build_ui()
        self.clock = QTimer(self); self.clock.timeout.connect(self.refresh_status); self.clock.start(1500); self.refresh_status()
        QShortcut(QKeySequence("Meta+E"), self, activated=self.open_explorer)
        QShortcut(QKeySequence("Ctrl+Alt+T"), self, activated=self.open_terminal)

    def build_ui(self):
        root = QWidget(); layout = QVBoxLayout(root); layout.setContentsMargins(0, 0, 0, 12); layout.setSpacing(0)
        canvas_layout = QVBoxLayout(self.canvas); canvas_layout.setContentsMargins(24, 20, 24, 20); canvas_layout.setSpacing(14)
        header = QHBoxLayout(); brand = QLabel("V/ELTRIX"); brand.setStyleSheet("font-size:20px;font-weight:900;color:white;letter-spacing:1px;")
        header.addWidget(brand); header.addStretch(); host = QLabel(platform.system() + "  •  DESKTOP")
        host.setStyleSheet("color:white;font-size:11px;font-weight:700;"); header.addWidget(host); canvas_layout.addLayout(header)
        content = QHBoxLayout(); content.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        icons = QVBoxLayout(); icons.setSpacing(8)
        for emoji, title, action in (("🖥️", "Ten komputer", self.show_system), ("📁", "Eksplorator", self.open_explorer),
              ("🌐", "Przeglądarka", self.open_browser), ("🎮", "Gaming Hub", self.open_gaming), ("⚙️", "Ustawienia", self.open_settings)):
            btn = QPushButton(f"{emoji}\n{title}"); btn.setObjectName("desktopIcon"); btn.setFixedSize(112, 78); btn.clicked.connect(action); icons.addWidget(btn)
        icons.addStretch(); content.addLayout(icons)
        card = QFrame(objectName="glass"); card.setMaximumWidth(590); card.setStyleSheet("QFrame#glass{background:rgba(12,18,29,205);border:1px solid rgba(255,255,255,60);border-radius:18px;}")
        box = QVBoxLayout(card); box.setContentsMargins(26, 22, 26, 22); box.addWidget(QLabel("YOUR DESKTOP, YOUR RULES", styleSheet="color:#c6ff6a;font-weight:800;letter-spacing:2px;"))
        box.addWidget(QLabel("Witaj w VELTRIX.", styleSheet="font-size:30px;font-weight:700;color:white;"))
        blurb = QLabel("Aplikacje, pliki, terminal i przeglądarka w jednym miejscu. Zbudowane z myślą o Twoim komputerze."); blurb.setWordWrap(True); blurb.setStyleSheet("color:#d2d9e3;"); box.addWidget(blurb)
        actions = QHBoxLayout()
        for label, action in (("Otwórz Eksplorator", self.open_explorer), ("Otwórz przeglądarkę", self.open_browser), ("Gaming Hub", self.open_gaming)):
            btn = QPushButton(label); btn.setObjectName("primary" if label.startswith("Otwórz") else ""); btn.clicked.connect(action); actions.addWidget(btn)
        box.addLayout(actions); content.addSpacing(18); content.addWidget(card, 0, Qt.AlignmentFlag.AlignTop); content.addStretch(); canvas_layout.addLayout(content, 1)
        bar = QFrame(objectName="taskbar"); bar.setFixedHeight(64); bar.setStyleSheet("QFrame#taskbar{background:rgba(18,24,34,238);border:1px solid rgba(255,255,255,45);border-radius:18px;}")
        row = QHBoxLayout(bar); row.setContentsMargins(12, 8, 14, 8)
        start = QPushButton("⊞"); start.setObjectName("primary"); start.setFixedSize(46, 44); start.clicked.connect(self.start_menu); row.addWidget(start)
        self.search = QLineEdit(); self.search.setPlaceholderText("Szukaj aplikacji lub wpisz adres…"); self.search.setFixedWidth(300); self.search.returnPressed.connect(self.search_action); row.addWidget(self.search)
        for label, action, tip in (("📁", self.open_explorer, "Eksplorator"), ("🌐", self.open_browser, "Przeglądarka"), (">_", self.open_terminal, "Terminal"), ("🎮", self.open_gaming, "Gaming"), ("⚙", self.open_settings, "Ustawienia")):
            btn=QPushButton(label); btn.setToolTip(tip); btn.setFixedSize(44, 44); btn.clicked.connect(action); row.addWidget(btn)
        row.addStretch(); self.status=QLabel(""); row.addWidget(self.status); self.time=QLabel(""); row.addWidget(self.time)
        layout.addWidget(self.canvas, 1); layout.addWidget(bar, 0, Qt.AlignmentFlag.AlignHCenter); self.setCentralWidget(root)

    def start_menu(self):
        menu=QMenu(self); menu.setMinimumWidth(290)
        title=QAction("VELTRIX  •  Aplikacje", menu); title.setEnabled(False); menu.addAction(title); menu.addSeparator()
        for label, action in (("📁  Eksplorator plików", self.open_explorer), ("🌐  Przeglądarka", self.open_browser), (">_  Terminal  (/help)", self.open_terminal), ("🎮  Gaming Hub", self.open_gaming), ("⚙  Ustawienia", self.open_settings), ("🖥️  Informacje o systemie", self.show_system)):
            menu.addAction(label, action)
        menu.addSeparator(); menu.addAction("Zamknij VELTRIX", self.close); menu.exec(self.sender().mapToGlobal(self.sender().rect().topLeft()))

    def search_action(self):
        text=self.search.text().strip(); self.search.clear(); q=text.casefold()
        if any(x in q for x in ("browser", "przegl", "internet", "http://", "https://")): self.open_browser(text if ":" in text or "." in text else "")
        elif any(x in q for x in ("explorer", "plik", "folder")): self.open_explorer()
        elif "terminal" in q or q=="cmd": self.open_terminal()
        elif any(x in q for x in ("gaming", "steam", "gry")): self.open_gaming()
        elif "ustaw" in q or "settings" in q: self.open_settings()
        elif q: self.open_browser("https://duckduckgo.com/?q=" + QUrl.toPercentEncoding(text).data().decode())

    def show_window(self, window):
        self.windows.append(window); window.destroyed.connect(lambda: self.windows.remove(window) if window in self.windows else None)
        window.show(); window.raise_(); window.activateWindow()

    def open_explorer(self, path=""):
        window=Explorer(self); self.show_window(window)
        if path: window.navigate(path)

    def open_browser(self, url=""):
        self.show_window(Browser(self, url or "https://duckduckgo.com"))

    def open_terminal(self): self.show_window(Terminal(self, self.open_browser, self.open_explorer, self.set_theme))

    def open_gaming(self):
        try: subprocess.Popen([sys.executable, "-m", "veltrix"], cwd=ROOT)
        except OSError as error: QMessageBox.critical(self, "Gaming Hub", str(error))

    def open_settings(self):
        dialog=QMainWindow(self, Qt.WindowType.Window); dialog.setWindowTitle("Ustawienia VELTRIX"); dialog.resize(500, 300)
        center=QWidget(); layout=QVBoxLayout(center); layout.setContentsMargins(24,24,24,24)
        heading=QLabel("Ustawienia"); heading.setObjectName("heading"); layout.addWidget(heading)
        box=QFrame(objectName="panel"); b=QVBoxLayout(box); b.addWidget(QLabel("Personalizacja")); theme=QCheckBox("Jasny motyw"); theme.setChecked(self.light); theme.toggled.connect(self.set_theme); b.addWidget(theme)
        b.addWidget(QLabel("VELTRIX to aplikacja użytkownika; uprawnienia i usługi systemowe kontroluje Windows/Linux.")); layout.addWidget(box); layout.addStretch()
        done=QPushButton("Gotowe"); done.clicked.connect(dialog.close); layout.addWidget(done); dialog.setCentralWidget(center); self.show_window(dialog)

    def set_theme(self, light): self.light=bool(light); self.setStyleSheet(LIGHT if self.light else DARK)

    def show_system(self):
        ram="brak danych"
        if psutil: ram=f"{psutil.virtual_memory().total/1024**3:.1f} GB"
        QMessageBox.information(self,"Ten komputer",f"System: {platform.platform()}\nProcesory: {os.cpu_count()}\nRAM: {ram}\nPython: {platform.python_version()}\n\nVELTRIX działa na istniejącym systemie.")

    def refresh_status(self):
        self.time.setText(datetime.now().strftime("%H:%M  •  %d.%m.%Y"))
        self.status.setText(f"CPU {psutil.cpu_percent():.0f}%  •  RAM {psutil.virtual_memory().percent:.0f}%" if psutil else "VELTRIX • gotowy")


def main():
    app=QApplication(sys.argv); app.setApplicationName("VELTRIX Desktop"); app.setStyle("Fusion")
    window=Desktop(); window.showMaximized(); return app.exec()


if __name__ == "__main__":
    try: raise SystemExit(main())
    except Exception:
        try: (HOME / "veltrix-desktop-startup.log").write_text(traceback.format_exc(), encoding="utf-8")
        except OSError: pass
        raise
