"""VELTRIX gaming desktop: a polished, cross-platform gaming dashboard."""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton,
    QProgressBar, QScrollArea, QSizePolicy, QStackedWidget, QVBoxLayout,
    QWidget,
)

try:
    import psutil
except ImportError:
    psutil = None

APP_TITLE = "VELTRIX // PLAY"
CONFIG_DIR = Path.home() / ".veltrix"
GAMES_FILE = CONFIG_DIR / "games.json"

DARK = "#090c12"
PANEL = "#111720"
PANEL_ALT = "#151e29"
BORDER = "#25313d"
TEXT = "#f2f6fa"
MUTED = "#8795a4"
ACCENT = "#a6ff00"
CYAN = "#44ddff"

STYLESHEET = f"""
QMainWindow, QWidget {{ background: {DARK}; color: {TEXT}; font-family: 'Segoe UI', sans-serif; }}
QFrame#sidebar {{ background: #0c1118; border-right: 1px solid {BORDER}; }}
QFrame#panel, QFrame#hero {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 14px; }}
QFrame#hero {{ background: #111b20; border: 1px solid #304131; }}
QLabel#muted {{ color: {MUTED}; }}
QLabel#eyebrow {{ color: {ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 2px; }}
QLabel#title {{ font-size: 30px; font-weight: 700; }}
QLabel#metric {{ color: {ACCENT}; font-size: 25px; font-weight: 700; }}
QPushButton {{ background: {PANEL_ALT}; color: {TEXT}; border: 1px solid {BORDER};
  border-radius: 9px; padding: 10px 14px; text-align: left; font-weight: 600; }}
QPushButton:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}
QPushButton#primary {{ background: {ACCENT}; color: #10150a; border: none; font-weight: 800; }}
QPushButton#primary:hover {{ background: #c1ff4c; color: #10150a; }}
QPushButton#nav {{ background: transparent; border: none; padding: 12px; color: {MUTED}; }}
QPushButton#nav:hover, QPushButton#nav[active="true"] {{ background: #18221b; color: {ACCENT}; }}
QListWidget {{ background: {PANEL}; border: 1px solid {BORDER}; border-radius: 10px; padding: 6px; }}
QListWidget::item {{ padding: 13px; border-radius: 7px; }}
QListWidget::item:selected {{ background: #23301e; color: {ACCENT}; }}
QProgressBar {{ background: #202a35; border: none; border-radius: 5px; height: 10px; text-align: center; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 5px; }}
QScrollArea {{ border: none; }}
"""


def load_games():
    try:
        data = json.loads(GAMES_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def save_games(games):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    GAMES_FILE.write_text(json.dumps(games, indent=2, ensure_ascii=False), encoding="utf-8")


def steam_roots():
    roots = []
    home = Path.home()
    if sys.platform == "win32":
        for raw in (os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                    os.environ.get("PROGRAMFILES", r"C:\Program Files")):
            roots.append(Path(raw) / "Steam")
        local = os.environ.get("LOCALAPPDATA")
        if local:
            roots.append(Path(local) / "Programs" / "Steam")
    elif sys.platform == "darwin":
        roots.append(home / "Library" / "Application Support" / "Steam")
    else:
        roots.extend((home / ".steam" / "steam", home / ".local" / "share" / "Steam",
                      home / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam"))
    return [p for p in roots if p.is_dir()]


def discover_steam_games():
    """Read local Steam app manifests; this only reads files and never changes Steam."""
    found = {}
    for root in steam_roots():
        libraries = {root}
        vdf = root / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            try:
                for path in re.findall(r'"path"\s*"([^"]+)"', vdf.read_text(encoding="utf-8", errors="ignore")):
                    libraries.add(Path(path.replace("\\\\", "\\")))
            except OSError:
                pass
        for library in libraries:
            for manifest in (library / "steamapps").glob("appmanifest_*.acf"):
                try:
                    text = manifest.read_text(encoding="utf-8", errors="ignore")
                    appid = re.search(r'"appid"\s*"(\d+)"', text)
                    name = re.search(r'"name"\s*"([^"]+)"', text)
                    if appid and name:
                        found[appid.group(1)] = {"name": name.group(1), "appid": appid.group(1), "path": ""}
                except OSError:
                    continue
    return list(found.values())


def gaming_checks():
    checks = []
    if sys.platform.startswith("linux"):
        checks.extend([
            ("System", "Ubuntu / Linux" if Path("/etc/os-release").exists() else "Linux"),
            ("Steam", "Gotowy" if shutil.which("steam") else "Nie znaleziono w PATH"),
            ("GameMode", "Gotowy" if shutil.which("gamemoded") or shutil.which("gamemoderun") else "Opcjonalny • nie wykryto"),
            ("MangoHud", "Gotowy" if shutil.which("mangohud") else "Opcjonalny • nie wykryto"),
        ])
    elif sys.platform == "win32":
        checks.extend([
            ("System", f"Windows {platform.release()}"),
            ("Steam", "Zainstalowany" if steam_roots() else "Nie wykryto standardowej instalacji"),
            ("GameMode", "Funkcja Linux • niedostępna w Windows"),
            ("MangoHud", "Funkcja Linux • niedostępna w Windows"),
        ])
    else:
        checks.append(("System", platform.platform()))
    return checks


class Card(QFrame):
    def __init__(self, title, value="", detail=""):
        super().__init__()
        self.setObjectName("panel")
        box = QVBoxLayout(self)
        box.setContentsMargins(18, 16, 18, 16)
        box.setSpacing(7)
        label = QLabel(title.upper())
        label.setObjectName("eyebrow")
        box.addWidget(label)
        self.value = QLabel(value)
        self.value.setObjectName("metric")
        self.value.setWordWrap(True)
        box.addWidget(self.value)
        self.detail = QLabel(detail)
        self.detail.setObjectName("muted")
        self.detail.setWordWrap(True)
        box.addWidget(self.detail)


class GamingDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1240, 800)
        self.setMinimumSize(900, 620)
        self.setStyleSheet(STYLESHEET)
        self.games = load_games()
        self.pages = QStackedWidget()
        self.nav_buttons = []

        shell = QWidget()
        row = QHBoxLayout(shell)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        sidebar = QFrame(objectName="sidebar")
        sidebar.setFixedWidth(220)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 24, 16, 18)
        brand = QLabel("V<span style='color:{ACCENT}'>/</span>ELTRIX")
        brand.setTextFormat(Qt.TextFormat.RichText)
        brand.setStyleSheet("font-size: 23px; font-weight: 900; letter-spacing: 1px;")
        side.addWidget(brand)
        tag = QLabel("PLAY SYSTEM")
        tag.setObjectName("eyebrow")
        side.addWidget(tag)
        side.addSpacing(32)
        for index, name in enumerate(("◈  Overview", "▣  Game Library", "⌁  Performance", "⚙  Gaming Setup")):
            button = QPushButton(name)
            button.setObjectName("nav")
            button.setProperty("active", index == 0)
            button.clicked.connect(lambda checked=False, i=index: self.navigate(i))
            side.addWidget(button)
            self.nav_buttons.append(button)
        side.addStretch()
        side.addWidget(QLabel("UBUNTU-INSPIRED • GAME-READY", objectName="muted"))
        row.addWidget(sidebar)
        row.addWidget(self.pages, 1)
        self.setCentralWidget(shell)

        self.pages.addWidget(self.make_overview())
        self.pages.addWidget(self.make_library())
        self.pages.addWidget(self.make_performance())
        self.pages.addWidget(self.make_setup())
        self.navigate(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_metrics)
        self.timer.start(1500)
        self.refresh_metrics()

    def page(self, eyebrow, title, description):
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(32, 27, 32, 28)
        layout.setSpacing(18)
        e = QLabel(eyebrow.upper())
        e.setObjectName("eyebrow")
        t = QLabel(title)
        t.setObjectName("title")
        d = QLabel(description)
        d.setObjectName("muted")
        d.setWordWrap(True)
        layout.addWidget(e)
        layout.addWidget(t)
        layout.addWidget(d)
        return host, layout

    def make_overview(self):
        host, layout = self.page("Your gaming hub", "Ready when you are.", "A clean control room for your games, system health, and Linux gaming tools.")
        hero = QFrame(objectName="hero")
        h = QHBoxLayout(hero)
        h.setContentsMargins(24, 22, 24, 22)
        intro = QVBoxLayout()
        badge = QLabel("●  VELTRIX GAMING MODE")
        badge.setObjectName("eyebrow")
        intro.addWidget(badge)
        headline = QLabel("Less setup.\nMore play.")
        headline.setStyleSheet("font-size: 34px; font-weight: 800;")
        intro.addWidget(headline)
        sub = QLabel("Ubuntu-inspired gaming dashboard for your existing Windows or Linux PC.")
        sub.setObjectName("muted")
        sub.setWordWrap(True)
        intro.addWidget(sub)
        h.addLayout(intro, 1)
        start = QPushButton("＋  ADD A GAME")
        start.setObjectName("primary")
        start.clicked.connect(self.add_game)
        start.setMinimumHeight(52)
        h.addWidget(start, 0, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(hero)

        grid = QGridLayout()
        grid.setSpacing(13)
        self.game_count_card = Card("Your library", str(len(self.games)), "Games ready to launch")
        self.cpu_card = Card("CPU load", "—", "Live system sample")
        self.ram_card = Card("Memory", "—", "Live system sample")
        self.platform_card = Card("Platform", platform.system(), platform.release())
        for i, card in enumerate((self.game_count_card, self.cpu_card, self.ram_card, self.platform_card)):
            grid.addWidget(card, 0, i)
        layout.addLayout(grid)
        section = QLabel("QUICK ACTIONS")
        section.setObjectName("eyebrow")
        layout.addWidget(section)
        actions = QHBoxLayout()
        for title, callback in (("▣  Open game library", lambda: self.navigate(1)),
                                ("⌁  Check performance", lambda: self.navigate(2)),
                                ("⚙  Gaming setup", lambda: self.navigate(3))):
            button = QPushButton(title)
            button.setMinimumHeight(56)
            button.clicked.connect(callback)
            actions.addWidget(button)
        layout.addLayout(actions)
        layout.addStretch()
        return host

    def make_library(self):
        host, layout = self.page("Your collection", "Game library", "Add a Windows executable or discover games from your local Steam library.")
        actions = QHBoxLayout()
        add = QPushButton("＋  Add executable")
        add.setObjectName("primary")
        add.clicked.connect(self.add_game)
        scan = QPushButton("↻  Scan Steam")
        scan.clicked.connect(self.scan_steam)
        launch = QPushButton("▶  Launch selected")
        launch.setObjectName("primary")
        launch.clicked.connect(self.launch_selected)
        remove = QPushButton("Remove")
        remove.clicked.connect(self.remove_selected)
        for button in (add, scan, launch, remove):
            actions.addWidget(button)
        layout.addLayout(actions)
        self.game_list = QListWidget()
        self.game_list.setSpacing(4)
        self.game_list.itemDoubleClicked.connect(lambda _item: self.launch_selected())
        layout.addWidget(self.game_list, 1)
        self.populate_games()
        hint = QLabel("Steam entries launch through Steam. Executables are launched directly; VELTRIX does not modify game files or system settings.")
        hint.setObjectName("muted")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        return host

    def make_performance(self):
        host, layout = self.page("Live system telemetry", "Performance", "Lightweight local monitoring. No data leaves this computer.")
        self.cpu_value = QLabel("—")
        self.ram_value = QLabel("—")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        for title, value, bar in (("CPU utilization", self.cpu_value, self.cpu_bar),
                                  ("Memory utilization", self.ram_value, self.ram_bar)):
            card = QFrame(objectName="panel")
            box = QVBoxLayout(card)
            box.setContentsMargins(20, 17, 20, 17)
            top = QHBoxLayout()
            label = QLabel(title)
            label.setObjectName("eyebrow")
            top.addWidget(label)
            top.addStretch()
            value.setObjectName("metric")
            top.addWidget(value)
            box.addLayout(top)
            box.addWidget(bar)
            layout.addWidget(card)
        self.process_info = QLabel("")
        self.process_info.setObjectName("muted")
        self.process_info.setWordWrap(True)
        layout.addWidget(self.process_info)
        layout.addStretch()
        return host

    def make_setup(self):
        host, layout = self.page("Linux gaming tools", "Gaming setup", "Check common gaming components. VELTRIX only reports status; it will never run privileged commands or silently change your system.")
        self.check_rows = QVBoxLayout()
        layout.addLayout(self.check_rows)
        refresh = QPushButton("↻  Refresh checks")
        refresh.clicked.connect(self.refresh_setup)
        layout.addWidget(refresh, 0, Qt.AlignmentFlag.AlignLeft)
        note = QLabel("On Ubuntu, install Steam, GameMode, and MangoHud using Ubuntu's Software app or official package sources. Availability depends on your distro and hardware.")
        note.setWordWrap(True)
        note.setObjectName("muted")
        layout.addWidget(note)
        layout.addStretch()
        self.refresh_setup()
        return host

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        for i, button in enumerate(self.nav_buttons):
            button.setProperty("active", i == index)
            button.style().unpolish(button)
            button.style().polish(button)

    def populate_games(self):
        if not hasattr(self, "game_list"):
            return
        self.game_list.clear()
        for game in self.games:
            suffix = "Steam" if game.get("appid") else game.get("path", "")
            item = QListWidgetItem(f"  {game.get('name', 'Unknown game')}\n     {suffix}")
            item.setData(Qt.ItemDataRole.UserRole, game)
            self.game_list.addItem(item)
        if hasattr(self, "game_count_card"):
            self.game_count_card.value.setText(str(len(self.games)))

    def add_game(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose a game executable", str(Path.home()),
                                              "Applications (*.exe);;All files (*)" if sys.platform == "win32" else "Applications (*)")
        if not path:
            return
        game = {"name": Path(path).stem, "path": path, "appid": ""}
        if not any(item.get("path") == path for item in self.games):
            self.games.append(game)
            save_games(self.games)
            self.populate_games()

    def scan_steam(self):
        discovered = discover_steam_games()
        known = {game.get("appid") for game in self.games if game.get("appid")}
        new_games = [game for game in discovered if game["appid"] not in known]
        self.games.extend(new_games)
        save_games(self.games)
        self.populate_games()
        QMessageBox.information(self, "Steam scan", f"Found {len(discovered)} installed Steam games; added {len(new_games)} new entries.")

    def launch_selected(self):
        item = self.game_list.currentItem()
        if not item:
            QMessageBox.information(self, "Choose a game", "Select a game in your library first.")
            return
        game = item.data(Qt.ItemDataRole.UserRole)
        try:
            if game.get("appid"):
                QDesktopServices.openUrl(QUrl(f"steam://rungameid/{game['appid']}"))
            else:
                path = Path(game.get("path", ""))
                if not path.is_file():
                    raise FileNotFoundError(f"Game executable not found: {path}")
                if sys.platform == "win32":
                    os.startfile(str(path))
                else:
                    subprocess.Popen([str(path)], cwd=str(path.parent), start_new_session=True)
        except Exception as error:
            QMessageBox.critical(self, "Could not launch game", str(error))

    def remove_selected(self):
        item = self.game_list.currentItem()
        if not item:
            return
        game = item.data(Qt.ItemDataRole.UserRole)
        self.games = [g for g in self.games if not (g.get("path") == game.get("path") and g.get("appid") == game.get("appid"))]
        save_games(self.games)
        self.populate_games()

    def refresh_metrics(self):
        if psutil is None:
            cpu, ram, info = "N/A", "N/A", "Install requirements to enable live monitoring."
        else:
            cpu_num = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            cpu, ram = f"{cpu_num:.0f}%", f"{memory.percent:.0f}%"
            if hasattr(self, "cpu_bar"):
                self.cpu_bar.setValue(int(cpu_num))
                self.ram_bar.setValue(int(memory.percent))
            info = f"{psutil.cpu_count(logical=True) or 'Unknown'} logical CPU threads  •  {memory.total / (1024 ** 3):.1f} GB RAM"
        if hasattr(self, "cpu_value"):
            self.cpu_value.setText(cpu)
            self.ram_value.setText(ram)
            self.process_info.setText(info)
        if hasattr(self, "cpu_card"):
            self.cpu_card.value.setText(cpu)
            self.ram_card.value.setText(ram)

    def refresh_setup(self):
        if not hasattr(self, "check_rows"):
            return
        while self.check_rows.count():
            child = self.check_rows.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        for name, value in gaming_checks():
            row = QFrame(objectName="panel")
            h = QHBoxLayout(row)
            h.setContentsMargins(17, 13, 17, 13)
            label = QLabel(name)
            label.setStyleSheet("font-weight: 700;")
            status = QLabel(value)
            status.setObjectName("muted")
            status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            h.addWidget(label)
            h.addStretch()
            h.addWidget(status)
            self.check_rows.addWidget(row)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setFont(QFont("Segoe UI", 10))
    window = GamingDesktop()
    window.show()
    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        try:
            log = CONFIG_DIR / "startup.log"
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            log.write_text(traceback.format_exc(), encoding="utf-8")
        except OSError:
            pass
        raise
