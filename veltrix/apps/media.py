from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
class MediaPlayer(QWidget):
    def __init__(self):
        super().__init__(); l=QVBoxLayout(self); l.addWidget(QLabel("Odtwarzacz multimediów — backend QtMultimedia można dołączyć opcjonalnie.")); l.addWidget(QPushButton("Wybierz plik"))
