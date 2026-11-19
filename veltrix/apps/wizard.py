from PyQt6.QtWidgets import QWizard, QWizardPage, QLabel
class FirstRunWizard(QWizard):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Pierwsza konfiguracja VELTRIX"); page=QWizardPage(); page.setTitle("Witaj w VELTRIX OS"); page.setLayout(__import__('PyQt6').QtWidgets.QVBoxLayout()); page.layout().addWidget(QLabel("Skonfiguruj język, motyw i bezpieczeństwo.")); self.addPage(page)
