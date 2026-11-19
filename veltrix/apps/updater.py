import shutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
class Updater(QWidget):
    def __init__(self):
        super().__init__(); self.status=QLabel(); b=QPushButton("Sprawdź aktualizator"); b.clicked.connect(self.check); l=QVBoxLayout(self); l.addWidget(QLabel("Aktualizator systemu")); l.addWidget(b); l.addWidget(self.status)
    def check(self): self.status.setText("Backend aktualizacji: apt" if shutil.which("apt") else "Niewykryty")
