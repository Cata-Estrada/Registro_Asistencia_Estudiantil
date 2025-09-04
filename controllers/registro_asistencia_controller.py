from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate
from PyQt5.QtCore import QDate
from models.course import Course
from models.enrollment import Enrollment
from models.class_session import ClassSession
from models.attendance import Attendance


class ComboDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(["presente", "ausente", "tarde"])
        return combo

    def setEditorData(self, editor, index):
        value = index.data()
        i = editor.findText(value)
        if i >= 0:
            editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText())


class RegistroAsistenciaController(QtWidgets.QWidget):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi("views/registro_asistencia.ui", self)
        self.user_id = user_id
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nombre del Estudiante", "Número de identificación", "Estado"])
        self.tableView.setModel(self.model)

        self.load_courses()

        self.seleccione_curso.currentIndexChanged.connect(self.load_students_for_course)
        self.fecha_clase.dateChanged.connect(self.load_students_for_course)
        self.guardar_asistencia.clicked.connect(self.save_attendance)
        self.tableView.setItemDelegateForColumn(2, ComboDelegate())

        self.set_fecha_actual()

    def set_fecha_actual(self):
        self.fecha_clase.setDate(QDate.currentDate())

    def load_courses(self):
        self.seleccione_curso.clear()
        self.seleccione_curso.addItem("Seleccione un curso", None)

        courses = Course.get_all_by_user(user_id=self.user_id)
        for c in courses:
            self.seleccione_curso.addItem(c.course_name, c.course_id)

        self.seleccione_curso.setCurrentIndex(0)

    def load_students_for_course(self):
        self.model.setRowCount(0)

        course_id = self.seleccione_curso.currentData()
        if course_id is None:
            return

        fecha = self.fecha_clase.date().toString("yyyy-MM-dd")

        students = Enrollment.get_students_by_course(course_id)
        class_session = ClassSession.get_by_date_and_course(fecha, course_id)

        asistencia_por_cedula = {}
        if class_session:
            asistencias = Attendance.get_by_class(class_session.class_id)
            for a in asistencias:
                asistencia_por_cedula[a.student_id] = a.status

        for cedula, nombre in students:
            estado = asistencia_por_cedula.get(cedula, "presente")
            fila = [
                QStandardItem(nombre),
                QStandardItem(cedula),
                QStandardItem(estado)
            ]
            self.model.appendRow(fila)

    def save_attendance(self):
        fecha = self.fecha_clase.date().toString("yyyy-MM-dd")
        course_id = self.seleccione_curso.currentData()

        if course_id is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Seleccione un curso válido antes de guardar.")
            return

        class_session = ClassSession.get_by_date_and_course(fecha, course_id)
        if not class_session:
            class_session = ClassSession(class_date=fecha, course_id=course_id)
            class_session.save()

        for row in range(self.model.rowCount()):
            cedula = self.model.item(row, 1).text()
            estado = self.model.item(row, 2).text()
            attendance = Attendance(class_id=class_session.class_id, student_id=cedula, status=estado)
            attendance.save()

        QtWidgets.QMessageBox.information(self, "Guardado", "Registro de asistencia guardado correctamente")
        self.load_students_for_course()
