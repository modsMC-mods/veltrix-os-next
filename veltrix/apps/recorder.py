from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
class Recorder(QWidget):
    def __init__(self):
        super().__init__(); l=QVBoxLayout(self); l.addWidget(QLabel("Nagrywanie ekranu wymaga FFmpeg/PipeWire.")); l.addWidget(QPushButton("Sprawdź dostępność FFmpeg"))
