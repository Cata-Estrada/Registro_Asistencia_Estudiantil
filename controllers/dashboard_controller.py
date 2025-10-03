# controllers/dashboard_controller.py
from PyQt5 import QtWidgets, uic, QtCore
from controllers.registro_estudiantil_controller import RegistroEstudiantilController
from controllers.registro_asistencia_controller import RegistroAsistenciaController
from controllers.historial_controller import HistorialController
from controllers.reportes_controller import ReportesController
from controllers.curso_controller import CursoController
from utils.paths import rel_path

class DashboardController(QtWidgets.QWidget):
    logout_signal = QtCore.pyqtSignal()  # señal para logout

    def __init__(self, user_id=None):
        super().__init__()
        uic.loadUi(rel_path("views", "dashboard.ui"), self)


        # Inicializar mostrando sidebar completo y ocultando compacto
        self.icon_only_widget.setVisible(False)
        self.widget_2.setVisible(True)

        # Páginas
        self.page_curso = CursoController(user_id)
        self.page_inscripcion = RegistroEstudiantilController(user_id)
        self.page_asistencia = RegistroAsistenciaController(user_id)
        self.page_historial = HistorialController(user_id)
        self.page_reportes = ReportesController(user_id)

        # Insertar en orden en el stackedWidget (índices fijos 0..4)
        self.stackedWidget.insertWidget(0, self.page_curso)
        self.stackedWidget.insertWidget(1, self.page_inscripcion)
        self.stackedWidget.insertWidget(2, self.page_asistencia)
        self.stackedWidget.insertWidget(3, self.page_historial)
        self.stackedWidget.insertWidget(4, self.page_reportes)

        # Conexiones de navegación (menú abierto)
        self.curso_2.toggled.connect(lambda checked: self.setPage(0) if checked else None)
        self.registro_estudiantil_2.toggled.connect(lambda checked: self.setPage(1) if checked else None)
        self.registro_asistencia_2.toggled.connect(lambda checked: self.setPage(2) if checked else None)
        self.historial_3.toggled.connect(lambda checked: self.setPage(3) if checked else None)
        self.reportes_2.toggled.connect(lambda checked: self.setPage(4) if checked else None)

        # Conexiones de navegación (menú compacto)
        self.curso.toggled.connect(lambda checked: self.setPage(0) if checked else None)
        self.registro_estudiantil.toggled.connect(lambda checked: self.setPage(1) if checked else None)
        self.registro_asistencia.toggled.connect(lambda checked: self.setPage(2) if checked else None)
        self.historial_2.toggled.connect(lambda checked: self.setPage(3) if checked else None)
        self.reportes_3.toggled.connect(lambda checked: self.setPage(4) if checked else None)

        # Botones salir (menú abierto y compacto)
        self.salir_2.clicked.connect(self.handle_logout)  # menú abierto
        self.salir.clicked.connect(self.handle_logout)    # menú compacto

        # Botón hamburguesa para alternar sidebars
        self.hamburguesa.toggled.connect(self.toggle_sidebars)

        # Página por defecto
        self.curso_2.setChecked(True)
        self.stackedWidget.setCurrentIndex(0)

        # Callback: cuando se cree un curso en inscripciones → refrescar cursos
        self.page_inscripcion.set_curso_creado_callback(self.page_curso.on_curso_creado_externo)

    def toggle_sidebars(self, checked):
        """Alternar entre menú completo y menú compacto"""
        self.icon_only_widget.setVisible(checked)
        self.widget_2.setVisible(not checked)

    def setPage(self, index):
        """Cambiar página y disparar recargas necesarias"""
        self.stackedWidget.setCurrentIndex(index)

        if index == 1:
            self.page_inscripcion.load_courses()
        elif index == 2:
            self.page_asistencia.load_courses()
            self.page_asistencia.load_students_for_course()
        elif index == 3:
            self.page_historial.load_courses()
            self.page_historial.historial_por_curso()
        elif index == 4:
            self.page_reportes.load_courses()
            self.page_reportes.load_report()

    def handle_logout(self):
        """Emitir señal para que MainWindow vuelva al login"""
        self.logout_signal.emit()
        self.hide()  # opcional, para ocultar el dashboard hasta que MainWindow lo limpie
