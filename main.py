from PyQt5 import QtWidgets
from controllers.login_controller import LoginController
from controllers.register_controller import RegisterController
from controllers.dashboard_controller import DashboardController
from resources import resources_rc


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        self.login = LoginController(self.on_login_success, self.show_register)
        self.register = RegisterController(self.show_login)

        self.dashboard = None

        self.stackedWidget.addWidget(self.login)
        self.stackedWidget.addWidget(self.register)

        self.stackedWidget.setCurrentWidget(self.login)

    def show_register(self):
        self.register.clear_fields()
        self.stackedWidget.setCurrentWidget(self.register)

    def show_login(self):
        self.login.clear_fields()
        self.stackedWidget.setCurrentWidget(self.login)

    def on_login_success(self, user):
        if not user:
            return

        if not self.dashboard:
            self.dashboard = DashboardController(user.user_id)
            self.dashboard.logout_signal.connect(self.handle_logout)
            self.stackedWidget.addWidget(self.dashboard)

        self.stackedWidget.setCurrentWidget(self.dashboard)

    def handle_logout(self):
        self.show_login()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
