from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
class ImageViewer(QWidget):
    def __init__(self):
        super().__init__(); l=QVBoxLayout(self); l.addWidget(QLabel("Przeglądarka obrazów")); l.addWidget(QPushButton("Otwórz obraz"))
