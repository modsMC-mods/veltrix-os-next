from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
class Bluetooth(QWidget):
    def __init__(self):
        super().__init__(); l=QVBoxLayout(self); l.addWidget(QLabel("Bluetooth")); l.addWidget(QPushButton("Sprawdź bluetoothctl"))
