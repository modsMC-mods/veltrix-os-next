from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider
from PyQt6.QtCore import Qt
class Audio(QWidget):
    def __init__(self):
        super().__init__(); l=QVBoxLayout(self); l.addWidget(QLabel("Głośność")); slider=QSlider(Qt.Orientation.Horizontal); slider.setRange(0,100); slider.setValue(50); l.addWidget(slider)
