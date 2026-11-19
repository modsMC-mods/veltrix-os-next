"""Extra Windows-inspired apps and a practical command extension for VELTRIX."""
import ast
import operator
import os
import time
from pathlib import Path

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction, QGuiApplication, QKeySequence
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPushButton, QPlainTextEdit, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

try:
    import psutil
except ImportError:
    psutil = None

CONFIG = Path.home() / ".veltrix"
NOTES_DIR = CONFIG / "notes"


class Calculator(QMainWindow):
    """Small arithmetic calculator; evaluates only a strict AST allowlist."""
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("VELTRIX Calculator")
        self.resize(420, 190)
        center = QWidget()
        layout = QVBoxLayout(center)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(QLabel("Obliczenia • obsługa + − × ÷ nawiasów i potęg"))
        self.expr = QLineEdit()
        self.expr.setPlaceholderText("Np. (12 + 8) * 3")
        self.expr.returnPressed.connect(self.calculate)
        layout.addWidget(self.expr)
        self.result = QLabel("Wynik pojawi się tutaj")
        self.result.setStyleSheet("font-size:22px;font-weight:700;")
        layout.addWidget(self.result)
        button = QPushButton("Oblicz")
        button.clicked.connect(self.calculate)
        layout.addWidget(button)
        self.setCentralWidget(center)

    def calculate(self):
        operations = {
            ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
            ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod, ast.Pow: operator.pow,
            ast.UAdd: operator.pos, ast.USub: operator.neg,
        }

        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                if abs(node.value) > 10**12:
                    raise ValueError("Liczba poza dozwolonym zakresem.")
                return node.value
            if isinstance(node, ast.UnaryOp) and type(node.op) in operations:
                return operations[type(node.op)](visit(node.operand))
            if isinstance(node, ast.BinOp) and type(node.op) in operations:
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Pow) and abs(right) > 12:
                    raise ValueError("Wykładnik może mieć maksymalnie wartość 12.")
                result = operations[type(node.op)](left, right)
                if abs(result) > 10**100:
                    raise ValueError("Wynik poza dozwolonym zakresem.")
                return result
            raise ValueError("Dozwolone są wyłącznie liczby, nawiasy i podstawowe działania.")

        try:
            tree = ast.parse(self.expr.text(), mode="eval")
            self.result.setText(f"= {visit(tree):,.10g}")
        except Exception as error:
            self.result.setText(f"Błąd: {error}")


class Notes(QMainWindow):
    """Autosaving local notes editor."""
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("VELTRIX Notes")
        self.resize(720, 520)
        NOTES_DIR.mkdir(parents=True, exist_ok=True)
        self.file = NOTES_DIR / "quick-note.txt"
        center = QWidget()
        layout = QVBoxLayout(center)
        layout.setContentsMargins(16, 16, 16, 16)
        top = QHBoxLayout()
        heading = QLabel("Notes")
        heading.setStyleSheet("font-size:22px;font-weight:700;")
        top.addWidget(heading)
        top.addStretch()
        self.status = QLabel("Zapis lokalny")
        top.addWidget(self.status)
        save = QPushButton("Zapisz teraz")
        save.clicked.connect(self.save)
        top.addWidget(save)
        layout.addLayout(top)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Zapisz tutaj notatkę…")
        self.editor.setPlainText(initial_text or self.load())
        self.editor.textChanged.connect(self.queue_save)
        layout.addWidget(self.editor, 1)
        self.setCentralWidget(center)
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save)
        QKeySequence.Save  # Keep the standard shortcut discoverable in the UI.
        self.editor.textChanged.connect(lambda: self.setWindowTitle("VELTRIX Notes • niezapisane"))

    def load(self):
        try:
            return self.file.read_text(encoding="utf-8")
        except OSError:
            return ""

    def queue_save(self):
        self.status.setText("Zapisywanie…")
        self.save_timer.start(500)

    def save(self):
        try:
            self.file.write_text(self.editor.toPlainText(), encoding="utf-8")
            self.status.setText(f"Zapisano • {self.file}")
            self.setWindowTitle("VELTRIX Notes")
        except OSError as error:
            self.status.setText(f"Błąd zapisu: {error}")


class ProcessManager(QMainWindow):
    """Read-only process overview; avoids unsafe terminate buttons."""
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("VELTRIX • Procesy")
        self.resize(760, 520)
        center = QWidget()
        layout = QVBoxLayout(center)
        layout.addWidget(QLabel("Procesy systemowe • podgląd tylko do odczytu"))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["PID", "Proces", "CPU %", "RAM %"])
        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 330)
        layout.addWidget(self.table, 1)
        refresh = QPushButton("Odśwież")
        refresh.clicked.connect(self.refresh)
        layout.addWidget(refresh)
        self.setCentralWidget(center)
        self.refresh()

    def refresh(self):
        self.table.setRowCount(0)
        if psutil is None:
            self.table.setRowCount(1)
            self.table.setItem(0, 1, QTableWidgetItem("Zainstaluj psutil, aby zobaczyć procesy."))
            return
        rows = []
        for proc in psutil.process_iter(["pid", "name", "memory_percent"]):
            try:
                rows.append((proc.info["pid"], proc.info["name"] or "?", proc.cpu_percent(None), proc.info["memory_percent"] or 0))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        for pid, name, cpu, memory in sorted(rows, key=lambda row: row[2], reverse=True)[:100]:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, value in enumerate((pid, name, f"{cpu:.1f}", f"{memory:.1f}")):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))


def safe_calculate(expression):
    """Return a safe numeric expression result without eval/exec."""
    window = Calculator()
    window.expr.setText(expression)
    window.calculate()
    result = window.result.text()
    window.close()
    if result.startswith("= "):
        return result[2:]
    raise ValueError(result.removeprefix("Błąd: ").strip())


def save_screenshot(parent=None):
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        QMessageBox.warning(parent, "Zrzut ekranu", "Nie wykryto ekranu.")
        return None
    default = str(Path.home() / "Pictures" / f"veltrix-{time.strftime('%Y%m%d-%H%M%S')}.png")
    path, _ = QFileDialog.getSaveFileName(parent, "Zapisz zrzut ekranu", default, "PNG image (*.png)")
    if not path:
        return None
    if not path.lower().endswith(".png"):
        path += ".png"
    if screen.grabWindow(0).save(path, "PNG"):
        return path
    QMessageBox.critical(parent, "Zrzut ekranu", "Nie udało się zapisać obrazu.")
    return None
