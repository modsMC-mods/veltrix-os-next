from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox
from veltrix.core.offline import set_offline
class ControlCenter(QWidget):
    def __init__(self):
        super().__init__(); layout=QVBoxLayout(self); layout.addWidget(QLabel("Centrum sterowania")); offline=QCheckBox("Tryb offline"); offline.toggled.connect(set_offline); layout.addWidget(offline); layout.addWidget(QPushButton("Ustawienia systemu"))
