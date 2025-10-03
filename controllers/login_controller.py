from PyQt5 import QtWidgets, uic
from models.user import User
from utils.paths import rel_path


class LoginController(QtWidgets.QWidget):
    def __init__(self, on_login_success, on_show_register):
        super().__init__()
        uic.loadUi(rel_path("views", "login.ui"), self)
        self.contrasena.setEchoMode(QtWidgets.QLineEdit.Password)
        self.iniciar_sesion.setFlat(False)
        self.registrar_aqui.setFlat(False)

        self.registrar_aqui.clicked.connect(on_show_register)
        self.iniciar_sesion.clicked.connect(self.handle_login)
        self.on_login_success = on_login_success

    def handle_login(self):
        identificador = self.correo.text().strip()
        contrasena = self.contrasena.text().strip()
        user = User.find_by_username_or_email(identificador)
        if user and user.password == contrasena:
            QtWidgets.QMessageBox.information(self, "Éxito", "Sesión iniciada correctamente")
            self.on_login_success(user)
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Credenciales incorrectas")

    def clear_fields(self):
        self.correo.clear()
        self.contrasena.clear()
