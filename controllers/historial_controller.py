from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QDate
from models.course import Course
from models.attendance import Attendance


class HistorialController(QtWidgets.QWidget):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi("views/historial.ui", self)
        self.user_id = user_id

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nombre Estudiante", "Fecha", "Número de identificación", "Estado"])
        self.tableView.setModel(self.model)

        self.load_courses()

        self.seleccione_curso.currentIndexChanged.connect(self.historial_por_curso)
        self.fecha_asistencia.dateChanged.connect(self.historial_por_fecha)
        self.buscar.clicked.connect(self.historial_por_nombre)

        self.set_fecha_actual()

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

    def historial_por_curso(self):
        self.model.setRowCount(0)
        course_id = self.seleccione_curso.itemData(self.seleccione_curso.currentIndex())

        if course_id is None:
            return

        rows = Attendance.get_historial(course_id)
        for r in rows:
            fila = [
                QStandardItem(r[0]),  # nombre_estudiante
                QStandardItem(r[1]),  # fecha_clase
                QStandardItem(r[2]),  # cedula
                QStandardItem(r[3])   # estado
            ]
            self.model.appendRow(fila)

    def historial_por_fecha(self):
        self.model.setRowCount(0)
        course_id = self.seleccione_curso.itemData(self.seleccione_curso.currentIndex())
        fecha = self.fecha_asistencia.date().toString("yyyy-MM-dd")

        if course_id is None or not fecha:
            return

        rows = Attendance.get_historial(course_id, fecha=fecha)
        for r in rows:
            fila = [
                QStandardItem(r[0]),
                QStandardItem(r[1]),
                QStandardItem(r[2]),
                QStandardItem(r[3])
            ]
            self.model.appendRow(fila)

    def historial_por_nombre(self):
        self.model.setRowCount(0)
        course_id = self.seleccione_curso.itemData(self.seleccione_curso.currentIndex())
        nombre = self.nombre_estudiante.text().strip()

        if course_id is None or not nombre:
            return

        rows = Attendance.get_historial(course_id, nombre_estudiante=nombre)
        for r in rows:
            fila = [
                QStandardItem(r[0]),
                QStandardItem(r[1]),
                QStandardItem(r[2]),
                QStandardItem(r[3])
            ]
            self.model.appendRow(fila)
