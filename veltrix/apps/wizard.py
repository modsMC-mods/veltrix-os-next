from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWizard, QWizardPage


class FirstRunWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pierwsza konfiguracja VELTRIX")
        page = QWizardPage()
        page.setTitle("Witaj w VELTRIX OS")
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Skonfiguruj język, motyw i ustawienia bezpieczeństwa."))
        page.setLayout(layout)
        self.addPage(page)
