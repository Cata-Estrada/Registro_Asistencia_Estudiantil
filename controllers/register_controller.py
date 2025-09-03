from PyQt5 import QtWidgets, uic
from models.user import User
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class RegisterController(QtWidgets.QWidget):
    def __init__(self, on_register_done):
        super().__init__()
        uic.loadUi("views/register.ui", self)
        # Mostrar caracteres ocultos en el campo contraseña
        self.contrasena.setEchoMode(QtWidgets.QLineEdit.Password)

        self.registrarse.clicked.connect(self.handle_register)
        self.on_register_done = on_register_done

        # Conectar botón "Inicia sesión aquí" si existe
        if hasattr(self, "iniciar_sesion"):
            self.iniciar_sesion.clicked.connect(lambda: self.on_register_done())

    def handle_register(self):
        nombre = self.nombre.text().strip()
        correo = self.correo.text().strip()
        contrasena = self.contrasena.text().strip()
        if not nombre or not correo or not contrasena:
            QtWidgets.QMessageBox.warning(self, "Error", "Complete todos los campos")
            return

        # Verificar que usuario o correo no existan
        if User.find_by_username_or_email(nombre) or User.find_by_username_or_email(correo):
            QtWidgets.QMessageBox.warning(self, "Error", "El usuario o correo ya existe")
            return

        user = User(username=nombre, correo=correo, password=contrasena)
        user.save()
        QtWidgets.QMessageBox.information(self, "Éxito", "Usuario registrado")
        self.on_register_done()

    def clear_fields(self):
        self.nombre.clear()
        self.correo.clear()
        self.contrasena.clear()


