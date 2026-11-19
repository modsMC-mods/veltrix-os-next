"""VELTRIX Desktop: a polished user-space desktop shell for Windows and Linux.

This is an application running on the host OS, not a replacement for Windows/Linux.
"""
import os
import platform
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QDir, QProcess, QTimer, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QDesktopServices, QKeySequence, QLinearGradient, QPainter, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QInputDialog, QLabel, QLineEdit, QMainWindow, QMenu,
    QMessageBox, QPlainTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

try:
    import psutil
except ImportError:
    psutil = None

ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
ACCENT = "#a6ff00"
DARK_STYLE = """
QMainWindow, QWidget { background:#10141c; color:#f4f6fb; font-family:'Segoe UI',sans-serif; }
QFrame#taskbar, QFrame#glass, QFrame#panel { background:#171d29; border:1px solid #30394a; border-radius:14px; }
QLabel#muted { color:#aab4c5; }
QLabel#heading { font-size:25px; font-weight:700; }
QPushButton { background:#222a38; color:#f4f6fb; border:1px solid #394457; border-radius:9px; padding:9px 13px; }
QPushButton:hover { background:#303b4e; border-color:#a6ff00; }
QPushButton#primary { background:#a6ff00; color:#11150b; border:0; font-weight:800; }
QPushButton#primary:hover { background:#c2ff59; }
QPushButton#desktopIcon { background:transparent; border:1px solid transparent; padding:10px; text-align:center; }
QPushButton#desktopIcon:hover { background:rgba(255,255,255,35); border-color:rgba(255,255,255,65); }
QLineEdit, QTableWidget, QPlainTextEdit { background:#121720; color:#f4f6fb; border:1px solid #394457; border-radius:8px; padding:8px; selection-background-color:#47651a; }
QTableWidget { gridline-color:#283140; }
QHeaderView::section { background:#1b2330; color:#b8c2d2; border:0; padding:8px; }
QMenu { background:#171d29; color:#f4f6fb; border:1px solid #394457; padding:8px; }
QMenu::item { padding:9px 24px; border-radius:6px; }
QMenu::item:selected { background:#303b4e; color:#a6ff00; }
QCheckBox { spacing:9px; }
"""
LIGHT_STYLE = """
QMainWindow, QWidget { background:#f0f3f8; color:#202938; font-family:'Segoe UI',sans-serif; }
QFrame#taskbar, QFrame#glass, QFrame#panel { background:#f8faff; border:1px solid #d5dce7; border-radius:14px; }
QLabel#muted { color:#647187; }
QLabel#heading { font-size:25px; font-weight:700; }
QPushButton { background:#e9eef6; color:#202938; border:1px solid #d0d8e5; border-radius:9px; padding:9px 13px; }
QPushButton:hover { background:#dfe8f5; border-color:#709326; }
QPushButton#primary { background:#7cac20; color:white; border:0; font-weight:800; }
QPushButton#desktopIcon { background:transparent; border:1px solid transparent; padding:10px; text-align:center; }
QPushButton#desktopIcon:hover { background:rgba(30,50,80,25); border-color:rgba(30,50,80,55); }
QLineEdit, QTableWidget, QPlainTextEdit { background:white; color:#202938; border:1px solid #d0d8e5; border-radius:8px; padding:8px; selection-background-color:#cfe2ad; }
QTableWidget { gridline-color:#e1e6ee; }
QHeaderView::section { background:#e7edf5; color:#435066; border:0; padding:8px; }
QMenu { background:#f8faff; color:#202938; border:1px solid #d0d8e5; padding:8px; }
QMenu::item { padding:9px 24px; border-radius:6px; }
QMenu::item:selected { background:#e3ebd7; color:#496719; }
"""


class Wallpaper(QWidget):
    """Paint a vivid, lightweight abstract wallpaper without external assets."""
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#142a3e"))
        gradient.setColorAt(.48, QColor("#273752"))
        gradient.setColorAt(1, QColor("#472b4b"))
        painter.fillRect(self.rect(), gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(48, 187, 176, 75))
        painter.drawEllipse(int(self.width() * .56), -180, 680, 680)
        painter.setBrush(QColor(172, 255, 0, 25))
        painter.drawEllipse(int(self.width() * .67), int(self.height() * .43), 520, 520)
        painter.setBrush(QColor(255, 118, 166, 35))
        painter.drawEllipse(-230, int(self.height() * .53), 520, 520)
        painter.end()


class FileExplorer(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("VELTRIX Explorer")
        self.resize(900, 590)
        self.current_path = HOME
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 16, 18, 18)
        layout.setSpacing(12)

        title_row = QHBoxLayout()
        title = QLabel("Explorer")
        title.setObjectName("heading")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(QLabel("Twoje pliki • lokalnie"))
        layout.addLayout(title_row)

        toolbar = QHBoxLayout()
        for caption, callback in (("←", self.go_up), ("⌂ Home", self.go_home), ("Odśwież", self.refresh)):
            button = QPushButton(caption)
            button.clicked.connect(callback)
            toolbar.addWidget(button)
        self.path = QLineEdit(str(HOME))
        self.path.returnPressed.connect(lambda: self.navigate(self.path.text()))
        toolbar.addWidget(self.path, 1)
        go = QPushButton("Idź")
        go.clicked.connect(lambda: self.navigate(self.path.text()))
        toolbar.addWidget(go)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Szukaj w tym folderze…")
        self.search.textChanged.connect(self.filter_rows)
        toolbar.addWidget(self.search)
        layout.addLayout(toolbar)

        actions = QHBoxLayout()
        for caption, callback in (("＋ Nowy folder", self.new_folder), ("Otwórz", self.open_selected)):
            button = QPushButton(caption)
            button.clicked.connect(callback)
            actions.addWidget(button)
        actions.addStretch()
        self.status = QLabel("")
        self.status.setObjectName("muted")
        actions.addWidget(self.status)
        layout.addLayout(actions)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nazwa", "Typ", "Rozmiar", "Zmodyfikowano"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in (1, 2, 3):
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellDoubleClicked.connect(self.open_row)
        layout.addWidget(self.table, 1)
        self.setCentralWidget(central)
        self.navigate(str(HOME))
        QShortcut(QKeySequence("Alt+Up"), self, activated=self.go_up)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.focus_path)
        QShortcut(QKeySequence("F5"), self, activated=self.refresh)

    def navigate(self, value):
        path = Path(value).expanduser()
        try:
            if not path.is_dir():
                raise NotADirectoryError(str(path))
            self.current_path = path.resolve()
            self.path.setText(str(self.current_path))
            self.search.clear()
            self.table.setRowCount(0)
            entries = sorted(self.current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.casefold()))
            for entry in entries:
                try:
                    stat = entry.stat()
                    kind = "Folder" if entry.is_dir() else (entry.suffix[1:].upper() or "Plik")
                    size = "—" if entry.is_dir() else self.format_size(stat.st_size)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                except OSError:
                    kind, size, modified = "Niedostępny", "—", "—"
                row = self.table.rowCount()
                self.table.insertRow(row)
                name_item = QTableWidgetItem(("📁  " if entry.is_dir() else "📄  ") + entry.name)
                name_item.setData(Qt.ItemDataRole.UserRole, str(entry))
                self.table.setItem(row, 0, name_item)
                for col, value in enumerate((kind, size, modified), 1):
                    self.table.setItem(row, col, QTableWidgetItem(value))
            self.status.setText(f"{len(entries)} elementów")
        except (OSError, PermissionError) as error:
            QMessageBox.warning(self, "Nie można otworzyć folderu", f"{path}\n\n{error}")

    @staticmethod
    def format_size(size):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if size < 1024 or unit == "TB":
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024

    def filter_rows(self, text):
        query = text.casefold()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            self.table.setRowHidden(row, bool(query) and query not in item.text().casefold())

    def go_home(self):
        self.navigate(str(HOME))

    def go_up(self):
        if self.current_path.parent != self.current_path:
            self.navigate(str(self.current_path.parent))

    def refresh(self):
        self.navigate(str(self.current_path))

    def focus_path(self):
        self.path.setFocus()
        self.path.selectAll()

    def selected_path(self):
        row = self.table.currentRow()
        item = self.table.item(row, 0) if row >= 0 else None
        return Path(item.data(Qt.ItemDataRole.UserRole)) if item else None

    def open_selected(self):
        path = self.selected_path()
        if path:
            self.open_path(path)

    def open_row(self, row, column):
        item = self.table.item(row, 0)
        if item:
            self.open_path(Path(item.data(Qt.ItemDataRole.UserRole)))

    def open_path(self, path):
        if path.is_dir():
            self.navigate(str(path))
        else:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def new_folder(self):
        name, ok = QInputDialog.getText(self, "Nowy folder", "Nazwa folderu:")
        if not ok or not name.strip():
            return
        try:
            (self.current_path / name.strip()).mkdir()
            self.refresh()
        except OSError as error:
            QMessageBox.critical(self, "Nie można utworzyć folderu", str(error))


class TerminalWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("VELTRIX Terminal")
        self.resize(800, 500)
        self.cwd = HOME
        self.process = None
        center = QWidget()
        layout = QVBoxLayout(center)
        layout.setContentsMargins(16, 16, 16, 16)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("font-family:Consolas,monospace;font-size:13px;")
        self.output.appendPlainText("VELTRIX Terminal • działa jako bieżący użytkownik")
        self.output.appendPlainText(str(self.cwd))
        self.input = QLineEdit()
        self.input.setPlaceholderText("Polecenie… (Enter uruchamia)")
        self.input.returnPressed.connect(self.run_command)
        layout.addWidget(self.output, 1)
        layout.addWidget(self.input)
        self.setCentralWidget(center)

    def run_command(self):
        command = self.input.text().strip()
        if not command or self.process:
            return
        self.input.clear()
        self.output.appendPlainText(f"\n{self.cwd} > {command}")
        if command.casefold() in ("clear", "cls"):
            self.output.clear()
            return
        if command.casefold() == "cd" or command.casefold().startswith("cd "):
            target = command[2:].strip().strip('"') or str(HOME)
            path = Path(target).expanduser()
            if not path.is_absolute():
                path = self.cwd / path
            if path.is_dir():
                self.cwd = path.resolve()
                self.output.appendPlainText(str(self.cwd))
            else:
                self.output.appendPlainText(f"Folder nie istnieje: {path}")
            return
        process = QProcess(self)
        process.setWorkingDirectory(str(self.cwd))
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        if os.name == "nt":
            process.setProgram(os.environ.get("COMSPEC", "cmd.exe"))
            process.setArguments(["/d", "/s", "/c", command])
        else:
            process.setProgram(os.environ.get("SHELL", "/bin/bash"))
            process.setArguments(["-lc", command])
        process.readyReadStandardOutput.connect(lambda p=process: self.read_output(p))
        process.finished.connect(lambda code, status, p=process: self.finished(p, code))
        self.process = process
        self.input.setEnabled(False)
        process.start()

    def read_output(self, process):
        text = bytes(process.readAllStandardOutput()).decode(errors="replace")
        if text:
            self.output.moveCursor(self.output.textCursor().MoveOperation.End)
            self.output.insertPlainText(text)
            self.output.ensureCursorVisible()

    def finished(self, process, code):
        self.read_output(process)
        self.output.appendPlainText(f"[zakończono: {code}]")
        self.process = None
        self.input.setEnabled(True)
        self.input.setFocus()
        process.deleteLater()


class VeltrixDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VELTRIX Desktop")
        self.resize(1440, 900)
        self.setMinimumSize(980, 650)
        self.setStyleSheet(DARK_STYLE)
        self.children = []
        self.light_theme = False
        self.canvas = Wallpaper()
        self._build_desktop()
        self.clock = QTimer(self)
        self.clock.timeout.connect(self.update_clock)
        self.clock.start(1000)
        self.update_clock()
        self.metrics = QTimer(self)
        self.metrics.timeout.connect(self.update_status)
        self.metrics.start(2500)
        self.update_status()
        QShortcut(QKeySequence("Meta+E"), self, activated=self.open_explorer)
        QShortcut(QKeySequence("Ctrl+Alt+T"), self, activated=self.open_terminal)

    def _build_desktop(self):
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(0)
        self.canvas.setMinimumHeight(500)
        canvas_layout = QVBoxLayout(self.canvas)
        canvas_layout.setContentsMargins(24, 20, 24, 22)
        canvas_layout.setSpacing(12)

        header = QHBoxLayout()
        brand = QLabel("V/ELTRIX")
        brand.setStyleSheet("font-size:20px;font-weight:900;color:white;letter-spacing:1px;")
        header.addWidget(brand)
        header.addStretch()
        self.host_label = QLabel(platform.system() + "  •  VELTRIX USER DESKTOP")
        self.host_label.setStyleSheet("color:rgba(255,255,255,205);font-size:11px;font-weight:700;")
        header.addWidget(self.host_label)
        canvas_layout.addLayout(header)

        content = QHBoxLayout()
        content.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        shortcuts = QVBoxLayout()
        shortcuts.setSpacing(12)
        for emoji, title, action in (
            ("🖥️", "Ten komputer", self.show_system_info),
            ("📁", "Eksplorator", self.open_explorer),
            ("🌐", "Przeglądarka", self.open_browser),
            ("🎮", "Gaming Hub", self.open_gaming),
            ("⚙️", "Ustawienia", self.open_settings),
        ):
            button = QPushButton(f"{emoji}\n{title}")
            button.setObjectName("desktopIcon")
            button.setFixedSize(112, 82)
            button.clicked.connect(action)
            shortcuts.addWidget(button)
        shortcuts.addStretch()
        content.addLayout(shortcuts)

        welcome = QFrame(objectName="glass")
        welcome.setMaximumWidth(560)
        welcome.setStyleSheet("QFrame#glass { background:rgba(12,18,29,205); border:1px solid rgba(255,255,255,60); border-radius:18px; }")
        welcome_layout = QVBoxLayout(welcome)
        welcome_layout.setContentsMargins(26, 22, 26, 22)
        welcome_layout.setSpacing(10)
        tag = QLabel("YOUR DESKTOP, YOUR RULES")
        tag.setStyleSheet("color:#c6ff6a;font-weight:800;letter-spacing:2px;font-size:10px;")
        welcome_layout.addWidget(tag)
        welcome_layout.addWidget(QLabel("Witaj w VELTRIX.", styleSheet="font-size:30px;font-weight:700;color:white;"))
        subtitle = QLabel("Pulpit inspirowany Windows, z gamingowym charakterem. Pliki, aplikacje i terminal masz pod ręką.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color:#d2d9e3;font-size:13px;")
        welcome_layout.addWidget(subtitle)
        buttons = QHBoxLayout()
        for caption, action in (("Otwórz Explorer", self.open_explorer), ("Uruchom Gaming Hub", self.open_gaming)):
            button = QPushButton(caption)
            button.setObjectName("primary" if caption.startswith("Otwórz") else "")
            button.clicked.connect(action)
            buttons.addWidget(button)
        welcome_layout.addLayout(buttons)
        content.addSpacing(20)
        content.addWidget(welcome, 0, Qt.AlignmentFlag.AlignTop)
        content.addStretch()
        canvas_layout.addLayout(content, 1)

        taskbar = QFrame(objectName="taskbar")
        taskbar.setFixedHeight(62)
        taskbar.setStyleSheet("QFrame#taskbar { background:rgba(18,24,34,238); border:1px solid rgba(255,255,255,45); border-radius:18px; }")
        task = QHBoxLayout(taskbar)
        task.setContentsMargins(12, 8, 14, 8)
        start = QPushButton("⊞")
        start.setToolTip("Start / aplikacje")
        start.setObjectName("primary")
        start.setFixedSize(44, 42)
        start.clicked.connect(self.show_start_menu)
        task.addWidget(start)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Szukaj aplikacji lub wpisz nazwę…")
        self.search.setFixedWidth(280)
        self.search.returnPressed.connect(self.search_action)
        task.addWidget(self.search)
        for label, action in (("📁", self.open_explorer), (">_", self.open_terminal), ("🎮", self.open_gaming), ("⚙", self.open_settings)):
            button = QPushButton(label)
            button.setToolTip({"📁":"Eksplorator plików",">_":"Terminal","🎮":"Gaming Hub","⚙":"Ustawienia"}[label])
            button.setFixedSize(44, 42)
            button.clicked.connect(action)
            task.addWidget(button)
        task.addStretch()
        self.status_label = QLabel("●  Gotowy")
        self.status_label.setStyleSheet("color:#dce7f1;")
        task.addWidget(self.status_label)
        self.clock_label = QLabel("")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.clock_label.setStyleSheet("font-weight:700;color:white;padding-left:12px;")
        task.addWidget(self.clock_label)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(task, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(0, 0, 0, 12)
        self.setCentralWidget(root)

    def show_start_menu(self):
        menu = QMenu(self)
        menu.setMinimumWidth(280)
        title = QAction("VELTRIX  •  Aplikacje", menu)
        title.setEnabled(False)
        menu.addAction(title)
        menu.addSeparator()
        for label, action in (("📁   Eksplorator plików", self.open_explorer),
                              (">_   Terminal", self.open_terminal),
                              ("🎮   Gaming Hub", self.open_gaming),
                              ("⚙   Ustawienia", self.open_settings),
                              ("🖥️   Informacje o systemie", self.show_system_info)):
            item = menu.addAction(label)
            item.triggered.connect(action)
        menu.addSeparator()
        quit_action = menu.addAction("Zamknij VELTRIX")
        quit_action.triggered.connect(self.close)
        menu.exec(self.sender().mapToGlobal(self.sender().rect().topLeft()))

    def search_action(self):
        query = self.search.text().strip().casefold()
        self.search.clear()
        actions = {
            "explorer": self.open_explorer, "pliki": self.open_explorer, "folder": self.open_explorer,
            "terminal": self.open_terminal, "cmd": self.open_terminal,
            "gaming": self.open_gaming, "gry": self.open_gaming, "steam": self.open_gaming,
            "ustawienia": self.open_settings, "settings": self.open_settings,
            "system": self.show_system_info, "komputer": self.show_system_info,
        }
        for key, action in actions.items():
            if key in query:
                action()
                return
        if query.startswith("http://") or query.startswith("https://"):
            QDesktopServices.openUrl(QUrl(query))
        elif query:
            QMessageBox.information(self, "Wyszukiwanie", f"Nie znaleziono aplikacji „{query}”. Spróbuj: pliki, terminal, gaming, ustawienia.")

    def open_window(self, window_type):
        window = window_type(self)
        self.children.append(window)
        window.destroyed.connect(lambda: self.children.remove(window) if window in self.children else None)
        window.show()
        window.raise_()
        window.activateWindow()
        return window

    def open_explorer(self):
        self.open_window(FileExplorer)

    def open_terminal(self):
        self.open_window(TerminalWindow)

    def open_gaming(self):
        try:
            subprocess.Popen([sys.executable, "-m", "veltrix"], cwd=ROOT)
        except OSError as error:
            QMessageBox.critical(self, "Gaming Hub", f"Nie udało się uruchomić Gaming Hub:\n{error}")

    def open_browser(self):
        QDesktopServices.openUrl(QUrl("https://www.google.com"))

    def open_settings(self):
        dialog = QMainWindow(self, Qt.WindowType.Window)
        dialog.setWindowTitle("Ustawienia VELTRIX")
        dialog.resize(520, 360)
        center = QWidget()
        layout = QVBoxLayout(center)
        layout.setContentsMargins(24, 24, 24, 24)
        heading = QLabel("Personalizacja")
        heading.setObjectName("heading")
        layout.addWidget(heading)
        box = QFrame(objectName="panel")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(18, 18, 18, 18)
        box_layout.addWidget(QLabel("Motyw interfejsu"))
        theme = QCheckBox("Jasny motyw")
        theme.setChecked(self.light_theme)
        theme.toggled.connect(self.set_theme)
        box_layout.addWidget(theme)
        box_layout.addWidget(QLabel("VELTRIX to aplikacja działająca na Twoim systemie. Ustawienia systemowe i uprawnienia pozostają pod kontrolą Windows/Linux."))
        layout.addWidget(box)
        layout.addStretch()
        close_button = QPushButton("Gotowe")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignRight)
        dialog.setCentralWidget(center)
        self.children.append(dialog)
        dialog.destroyed.connect(lambda: self.children.remove(dialog) if dialog in self.children else None)
        dialog.show()

    def set_theme(self, light):
        self.light_theme = bool(light)
        self.setStyleSheet(LIGHT_STYLE if self.light_theme else DARK_STYLE)
        self.canvas.update()

    def show_system_info(self):
        ram = "Brak danych"
        if psutil is not None:
            vm = psutil.virtual_memory()
            ram = f"{vm.total / (1024 ** 3):.1f} GB"
        QMessageBox.information(self, "Ten komputer", f"VELTRIX Desktop\n\nSystem: {platform.platform()}\nPython: {platform.python_version()}\nPamięć RAM: {ram}\n\nVELTRIX nie jest systemem operacyjnym i nie zmienia systemu hosta.")

    def update_clock(self):
        self.clock_label.setText(datetime.now().strftime("%H:%M   •   %d.%m.%Y"))

    def update_status(self):
        if psutil is None:
            self.status_label.setText("●  VELTRIX ready")
        else:
            self.status_label.setText(f"●  CPU {psutil.cpu_percent():.0f}%  •  RAM {psutil.virtual_memory().percent:.0f}%")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VELTRIX Desktop")
    app.setStyle("Fusion")
    window = VeltrixDesktop()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        log = HOME / "veltrix-desktop-startup.log"
        try:
            log.write_text(traceback.format_exc(), encoding="utf-8")
        except OSError:
            pass
        raise
