from PyQt5 import QtWidgets, QtCore
from controllers.login_controller import LoginController
from controllers.register_controller import RegisterController
from controllers.dashboard_controller import DashboardController
from resources import resources_rc


def size_and_center(widget: QtWidgets.QWidget, w_ratio=0.7, h_ratio=0.7,
                    min_size=(900, 600), max_size=(1920, 1080)):
    screen = QtWidgets.QApplication.primaryScreen()
    geo = screen.availableGeometry() if screen else QtCore.QRect(0, 0, 1366, 768)

    # Tamaño objetivo
    target_w = int(geo.width() * w_ratio)
    target_h = int(geo.height() * h_ratio)

    # Respetar mínimos y máximos
    target_w = max(min_size[0], min(target_w, max_size[0]))
    target_h = max(min_size[1], min(target_h, max_size[1]))

    widget.resize(target_w, target_h)

    # Centrar
    frame_geo = widget.frameGeometry()
    center_point = geo.center()
    frame_geo.moveCenter(center_point)
    widget.move(frame_geo.topLeft())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        self.login = LoginController(self.on_login_success, self.show_register)
        self.register = RegisterController(self.show_login)

        self.dashboard = None  # se crea al loguear

        self.stackedWidget.addWidget(self.login)
        self.stackedWidget.addWidget(self.register)

        # Mostrar login al inicio
        self.stackedWidget.setCurrentWidget(self.login)

        # Ajustar tamaño inicial y centrar MainWindow
        size_and_center(self)

        # Opcional: fijar tamaño mínimo para que no se deforme
        self.setMinimumSize(900, 600)

    def show_register(self):
        self.register.clear_fields()
        self.stackedWidget.setCurrentWidget(self.register)
        self._center_current()

    def show_login(self):
        self.login.clear_fields()
        self.stackedWidget.setCurrentWidget(self.login)
        self._center_current()

    def on_login_success(self, user):
        if not user:
            return

        # Crear nuevo dashboard por sesión
        self.dashboard = DashboardController(user.user_id)
        self.dashboard.logout_signal.connect(self.handle_logout)

        # Agregarlo si no está en el stacked
        index = self.stackedWidget.indexOf(self.dashboard)
        if index == -1:
            self.stackedWidget.addWidget(self.dashboard)

        self.stackedWidget.setCurrentWidget(self.dashboard)
        self._center_current()

    def handle_logout(self):
        """Volver al login al dar clic en salir desde el dashboard"""
        self.show_login()

        # Destruir el dashboard para limpiar memoria
        if self.dashboard:
            self.stackedWidget.removeWidget(self.dashboard)
            self.dashboard.deleteLater()
            self.dashboard = None

    # -------- Helpers --------
    def _center_current(self):
        # Redimensiona y centra la ventana contenedora; los hijos están dentro del QStackedWidget
        size_and_center(self)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
