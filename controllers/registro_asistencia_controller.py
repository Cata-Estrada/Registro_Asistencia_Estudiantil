# controllers/registro_asistencia_controller.py
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate, QHeaderView
from PyQt5.QtCore import QDate, Qt
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


class CenterAlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter


class RegistroAsistenciaController(QtWidgets.QWidget):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi("views/registro_asistencia.ui", self)
        self.user_id = user_id

        # Modelo
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nombre del Estudiante", "Número de identificación", "Estado"])
        self.tableView.setModel(self.model)

        # Delegados
        self._center_delegate = CenterAlignDelegate(self.tableView)
        self.tableView.setItemDelegate(self._center_delegate)
        self.tableView.setItemDelegateForColumn(2, ComboDelegate())

        # Configurar tabla
        self._configure_table_columns()

        # Cargas y conexiones
        self.load_courses()
        self.seleccione_curso.currentIndexChanged.connect(self.load_students_for_course)
        self.fecha_clase.dateChanged.connect(self.load_students_for_course)
        self.guardar_asistencia.clicked.connect(self.save_attendance)
        self.set_fecha_actual()

    def _configure_table_columns(self):
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.verticalHeader().setVisible(False)

        hh = self.tableView.horizontalHeader()
        try:
            hh.setDefaultAlignment(Qt.AlignCenter)
        except AttributeError:
            pass

        # Proporcionalidad: todas las columnas con Stretch
        hh.setStretchLastSection(False)
        hh.setSectionResizeMode(0, QHeaderView.Stretch)  # Nombre
        hh.setSectionResizeMode(1, QHeaderView.Stretch)  # Identificación
        hh.setSectionResizeMode(2, QHeaderView.Stretch)  # Estado

        # Mínimos por columna para evitar recortes del encabezado
        self.tableView.setColumnWidth(0, 200)
        self.tableView.setColumnWidth(1, 200)
        self.tableView.setColumnWidth(2, 140)
        self.tableView.horizontalHeader().setMinimumSectionSize(120)

        # Selección y scroll
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked | QtWidgets.QAbstractItemView.SelectedClicked
        )
        self.tableView.verticalHeader().setDefaultSectionSize(28)
        self.tableView.setTextElideMode(Qt.ElideNone)

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
        """
        Cargar los estudiantes de la matrícula actualizada.
        Si ya existe asistencia, se usa el estado guardado.
        Si no, se asigna "presente" por defecto.
        """
        self.model.setRowCount(0)

        course_id = self.seleccione_curso.currentData()
        if course_id is None:
            return

        fecha = self.fecha_clase.date().toString("yyyy-MM-dd")

        # Obtener todos los estudiantes matriculados
        students = Enrollment.get_students_by_course(course_id)

        # Buscar sesión de clase (si existe)
        class_session = ClassSession.get_by_date_and_course(fecha, course_id)

        # Cargar asistencias existentes
        asistencia_por_cedula = {}
        if class_session:
            asistencias = Attendance.get_by_class(class_session.class_id)
            for a in asistencias:
                asistencia_por_cedula[a.student_id] = a.status

        # Crear filas → matrícula manda, asistencia complementa
        for cedula, nombre in students:
            estado = asistencia_por_cedula.get(cedula, "presente")
            fila = [
                QStandardItem(nombre),
                QStandardItem(cedula),
                QStandardItem(estado)
            ]
            fila[0].setEditable(False)
            fila[1].setEditable(False)
            for it in fila:
                it.setTextAlignment(Qt.AlignCenter)
            self.model.appendRow(fila)

        self._apply_proportional_resize()

    def _apply_proportional_resize(self):
        hh = self.tableView.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)

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
