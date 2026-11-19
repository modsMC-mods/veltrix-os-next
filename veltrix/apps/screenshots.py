from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QDateTime
class Screenshots(QWidget):
    def __init__(self):
        super().__init__(); b=QPushButton("Zapisz zrzut ekranu"); b.clicked.connect(self.capture); self.status=QLabel(); l=QVBoxLayout(self); l.addWidget(QLabel("Zrzuty ekranu")); l.addWidget(b); l.addWidget(self.status)
    def capture(self):
        screen=self.window().screen(); name=f"veltrix-{QDateTime.currentDateTime().toString('yyyyMMdd-hhmmss')}.png"; screen.grabWindow(0).save(name); self.status.setText(f"Zapisano: {name}")
