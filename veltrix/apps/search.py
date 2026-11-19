from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QListWidget
from veltrix.core.search import search
class Search(QWidget):
    def __init__(self):
        super().__init__(); self.root=QLineEdit(placeholderText="Szukaj w katalogu domowym"); self.results=QListWidget(); self.root.returnPressed.connect(self.run); l=QVBoxLayout(self); l.addWidget(QLabel("Wyszukiwanie globalne")); l.addWidget(self.root); l.addWidget(self.results)
    def run(self): self.results.clear(); self.results.addItems([str(p) for p in search("~", self.root.text())])
