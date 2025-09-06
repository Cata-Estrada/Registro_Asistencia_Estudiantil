from PyQt5 import QtWidgets, uic, QtCore
from controllers.registro_estudiantil_controller import RegistroEstudiantilController
from controllers.registro_asistencia_controller import RegistroAsistenciaController
from controllers.historial_controller import HistorialController
from controllers.reportes_controller import ReportesController


class DashboardController(QtWidgets.QWidget):
    logout_signal = QtCore.pyqtSignal()  # señal para logout

    def __init__(self, user_id=None):
        super().__init__()
        uic.loadUi("views/dashboard.ui", self)

        # Inicializar mostrando sidebar completo y ocultando compacto
        self.icon_only_widget.setVisible(False)
        self.widget_2.setVisible(True)

        # Carga las páginas internas
        self.page_inicio = QtWidgets.QWidget()
        uic.loadUi("views/inicio.ui", self.page_inicio)

        self.page_curso = QtWidgets.QWidget()
        uic.loadUi("views/curso.ui", self.page_curso)

        self.page_inscripcion = RegistroEstudiantilController(user_id)
        self.page_asistencia = RegistroAsistenciaController(user_id)
        self.page_historial = HistorialController(user_id)
        self.page_reportes = ReportesController(user_id)

        self.stackedWidget.insertWidget(0, self.page_inicio)
        self.stackedWidget.insertWidget(1, self.page_curso)
        self.stackedWidget.insertWidget(2, self.page_inscripcion)
        self.stackedWidget.insertWidget(3, self.page_asistencia)
        self.stackedWidget.insertWidget(4, self.page_historial)
        self.stackedWidget.insertWidget(5, self.page_reportes)

        # Conexiones botones para navegación
        self.inicio_2.toggled.connect(lambda checked: self.setPage(0) if checked else None)
        self.curso_2.toggled.connect(lambda checked: self.setPage(1) if checked else None)
        self.registro_estudiantil_2.toggled.connect(lambda checked: self.setPage(2) if checked else None)
        self.registro_asistencia_2.toggled.connect(lambda checked: self.setPage(3) if checked else None)
        self.historial_3.toggled.connect(lambda checked: self.setPage(4) if checked else None)
        self.reportes_2.toggled.connect(lambda checked: self.setPage(5) if checked else None)

        # Botón para cerrar sesión
        self.salir_2.clicked.connect(self.handle_logout)

        # Botón hamburguesa para alternar sidebars
        self.hamburguesa.toggled.connect(self.toggle_sidebars)

        self.inicio_2.setChecked(True)

    def toggle_sidebars(self, checked):
        # Mostrar sidebar compacto si hamburguesa está activado, sino sidebar completo
        self.icon_only_widget.setVisible(checked)
        self.widget_2.setVisible(not checked)

    def setPage(self, index):
        self.stackedWidget.setCurrentIndex(index)
        if index == 2:
            self.page_inscripcion.load_courses()
        elif index == 3:
            self.page_asistencia.load_courses()
            self.page_asistencia.load_students_for_course()
        elif index == 4:
            self.page_historial.load_courses()
            self.page_historial.historial_por_curso()
        elif index == 5:
            self.page_reportes.load_courses()
            self.page_reportes.load_report()

    def handle_logout(self):
        self.logout_signal.emit()
