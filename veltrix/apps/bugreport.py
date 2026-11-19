from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
class BugReport(QWidget):
    def __init__(self):
        super().__init__(); l=QVBoxLayout(self); l.addWidget(QLabel("Kreator raportu błędu")); l.addWidget(QLabel("Zbiera tylko dane diagnostyczne po zatwierdzeniu przez użytkownika."))
