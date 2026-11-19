from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
from veltrix.core.profiles import create_user, authenticate
class Login(QWidget):
    def __init__(self):
        super().__init__(); self.user=QLineEdit(placeholderText="Użytkownik"); self.password=QLineEdit(placeholderText="Hasło"); self.password.setEchoMode(QLineEdit.EchoMode.Password); self.status=QLabel(); login=QPushButton("Zaloguj"); login.clicked.connect(self.login); l=QVBoxLayout(self); [l.addWidget(x) for x in (QLabel("VELTRIX Login"),self.user,self.password,login,self.status)]
    def login(self): self.status.setText("Zalogowano" if authenticate(self.user.text(),self.password.text()) else "Nieprawidłowe dane")
