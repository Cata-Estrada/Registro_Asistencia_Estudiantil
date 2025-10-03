# controllers/historial_controller.py
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView, QStyledItemDelegate
from PyQt5.QtCore import QDate, Qt
from models.course import Course
from models.attendance import Attendance
from utils.export_utils import export_tableview_to_csv


class CenterAlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter


class HistorialController(QtWidgets.QWidget):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi("views/historial.ui", self)
        self.user_id = user_id

        self.headers = ["Nombre Estudiante", "Fecha", "Número de identificación", "Estado"]
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.headers)
        self.tableView.setModel(self.model)

        self._center_delegate = CenterAlignDelegate(self.tableView)
        self.tableView.setItemDelegate(self._center_delegate)

        self._configure_table_columns()
        self.load_courses()

        # 🔹 Filtros: curso -> historial completo; fecha -> solo esa fecha; búsqueda por nombre
        self.seleccione_curso.currentIndexChanged.connect(self.on_curso_cambiado)
        self.seleccione_curso.activated.connect(self.on_curso_cambiado)  # 👈 se ejecuta incluso si seleccionas el mismo curso

        self.fecha_asistencia.dateChanged.connect(self.on_fecha_cambiada)
        self.fecha_asistencia.userDateChanged.connect(self.on_fecha_cambiada)  # 👈 se ejecuta siempre que el usuario cambia la fecha
        self.fecha_asistencia.editingFinished.connect(self.on_fecha_cambiada)  # 👈 incluso si escribe la misma fecha

        self.buscar.clicked.connect(self.historial_por_nombre)

        if hasattr(self, "exportar_asistencia"):
            self.exportar_asistencia.clicked.connect(self._exportar_historial_csv)

        # Fecha por defecto al abrir
        self.set_fecha_actual()

    def _configure_table_columns(self):
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.verticalHeader().setVisible(False)

        hh = self.tableView.horizontalHeader()
        try:
            hh.setDefaultAlignment(Qt.AlignCenter)
        except AttributeError:
            pass

        hh.setStretchLastSection(False)
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)

        self.tableView.horizontalHeader().setMinimumSectionSize(120)
        self.tableView.setColumnWidth(0, 220)
        self.tableView.setColumnWidth(1, 160)
        self.tableView.setColumnWidth(2, 200)
        self.tableView.setColumnWidth(3, 140)

        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.verticalHeader().setDefaultSectionSize(28)
        self.tableView.setTextElideMode(Qt.ElideNone)

    def set_fecha_actual(self):
        self.fecha_asistencia.setDate(QDate.currentDate())

    def load_courses(self):
        self.seleccione_curso.clear()
        self.seleccione_curso.addItem("Seleccione curso", None)
        self.seleccione_curso.model().item(0).setEnabled(False)

        courses = Course.get_all_by_user(user_id=self.user_id)
        for curso in courses:
            self.seleccione_curso.addItem(curso.course_name, curso.course_id)

        self.seleccione_curso.setCurrentIndex(0)

    def _append_hist_row(self, r):
        fila = [QStandardItem(r[0]), QStandardItem(r[1]), QStandardItem(r[2]), QStandardItem(r[3])]
        for it in fila:
            it.setTextAlignment(Qt.AlignCenter)
        self.model.appendRow(fila)

    def historial_por_curso(self):
        self.on_curso_cambiado()

    def on_curso_cambiado(self):
        """Al elegir curso, mostrar TODO el historial del curso."""
        self.model.setRowCount(0)
        course_id = self.seleccione_curso.itemData(self.seleccione_curso.currentIndex())
        if course_id is None:
            return

        if hasattr(self, "nombre_estudiante"):
            self.nombre_estudiante.clear()

        # 🔹 Cargar historial completo del curso (SIN filtros de fecha)
        rows = Attendance.get_historial(course_id)
        for r in rows:
            self._append_hist_row(r)

    def on_fecha_cambiada(self):
        """Al cambiar la fecha, mostrar solo esa fecha para el curso actual."""
        self.model.setRowCount(0)
        course_id = self.seleccione_curso.itemData(self.seleccione_curso.currentIndex())
        if course_id is None:
            return
        fecha = self.fecha_asistencia.date().toString("yyyy-MM-dd")
        rows = Attendance.get_historial(course_id, fecha=fecha)
        for r in rows:
            self._append_hist_row(r)

    def historial_por_nombre(self):
        """Búsqueda por nombre dentro del curso actual."""
        self.model.setRowCount(0)
        course_id = self.seleccione_curso.itemData(self.seleccione_curso.currentIndex())
        nombre = self.nombre_estudiante.text().strip() if hasattr(self, "nombre_estudiante") else ""
        if course_id is None or not nombre:
            return

        rows = Attendance.get_historial(course_id, nombre_estudiante=nombre)
        for r in rows:
            self._append_hist_row(r)

    def _exportar_historial_csv(self):
        course_name = self.seleccione_curso.currentText().strip() or "curso"
        fecha_txt = self.fecha_asistencia.date().toString("yyyyMMdd")
        sugerido = f"historial_{course_name}_{fecha_txt}.csv".replace(" ", "_")
        export_tableview_to_csv(self.tableView, headers=self.headers, parent_widget=self, default_name=sugerido)
