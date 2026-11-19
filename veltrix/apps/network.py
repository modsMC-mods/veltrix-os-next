from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
class Network(QWidget):
    def __init__(self):
        super().__init__(); l=QVBoxLayout(self); l.addWidget(QLabel("Panel sieci Wi-Fi")); l.addWidget(QPushButton("Otwórz ustawienia sieci"))
