import shutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
class PackageManager(QWidget):
    def __init__(self):
        super().__init__(); self.status=QLabel(); b=QPushButton("Sprawdź apt"); b.clicked.connect(self.check); l=QVBoxLayout(self); l.addWidget(QLabel("Menedżer pakietów")); l.addWidget(b); l.addWidget(self.status)
    def check(self): self.status.setText("apt: dostępny" if shutil.which("apt") else "Brak apt — użyj menedżera dystrybucji")
