# controllers/registro_estudiantil_controller.py
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView, QStyledItemDelegate
from PyQt5.QtCore import Qt
from models.course import Course
from models.student import Student
from models.enrollment import Enrollment
# controllers/registro_estudiantil_controller.py
from utils.cvs_utils import cargar_estudiantes_desde_csv



class CenterAlignDelegate(QStyledItemDelegate):
    """Centra el texto en todas las celdas."""
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter


class RegistroEstudiantilController(QtWidgets.QWidget):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi("views/registro_estudiantil.ui", self)
        self.user_id = user_id

        # Callback opcional para informar creación de cursos a otras vistas (inyectado desde el Dashboard)
        self._curso_creado_cb = None

        # Modelo tabla estudiantes
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nombre del Estudiante", "Número de identificación"])
        self.tableView.setModel(self.model)

        # Delegado para centrar contenido
        self._center_delegate = CenterAlignDelegate(self.tableView)
        self.tableView.setItemDelegate(self._center_delegate)

        # Configurar columnas proporcionales y encabezados centrados
        self._configure_table_columns()

        # Cargar combos
        self.load_courses()

        # Conexiones
        self.agregar_curso.clicked.connect(self.add_course)
        self.cargar_lista_estudiantes.clicked.connect(self.cargar_estudiantes_csv)
        self.guardar_lista_curso.clicked.connect(self.save_students)

    # Suministrado por el Dashboard para sincronización en caliente
    def set_curso_creado_callback(self, cb):
        self._curso_creado_cb = cb

    def _configure_table_columns(self):
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.verticalHeader().setVisible(False)

        hh = self.tableView.horizontalHeader()
        try:
            hh.setDefaultAlignment(Qt.AlignCenter)
        except AttributeError:
            pass

        # Proporcionalidad: ambas columnas con Stretch
        hh.setStretchLastSection(False)
        hh.setSectionResizeMode(0, QHeaderView.Stretch)  # Nombre
        hh.setSectionResizeMode(1, QHeaderView.Stretch)  # Identificación

        # Mínimos para evitar recortes de títulos
        self.tableView.horizontalHeader().setMinimumSectionSize(140)
        self.tableView.setColumnWidth(0, 220)
        self.tableView.setColumnWidth(1, 220)

        # Selección por fila y sin elipsis
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.verticalHeader().setDefaultSectionSize(28)
        self.tableView.setTextElideMode(Qt.ElideNone)

    def load_courses(self):
        self.selecionar_curso.clear()
        self.selecionar_curso.addItem("Seleccione curso", None)
        self.selecionar_curso.model().item(0).setEnabled(False)

        courses = Course.get_all_by_user(user_id=self.user_id)
        for c in courses:
            self.selecionar_curso.addItem(c.course_name, c.course_id)

        self.selecionar_curso.setCurrentIndex(0)

    def add_course(self):
        course_name = self.nombre_curso.text().strip()
        if not course_name:
            QtWidgets.QMessageBox.warning(self, "Error", "Debe ingresar el nombre del curso")
            return

        # tipo vacío por ahora (puedes ajustar si manejas tipos)
        nuevo_curso = Course(course_name=course_name, course_type="", user_id=self.user_id)
        nuevo_curso.save()

        # Notificar inmediatamente a otros controladores (CursoController) vía callback
        if self._curso_creado_cb:
            self._curso_creado_cb(nuevo_curso)

        # Refrescar combo y limpiar campo
        self.nombre_curso.clear()
        self.load_courses()

        QtWidgets.QMessageBox.information(self, "Éxito", "Curso agregado correctamente")

    def cargar_estudiantes_csv(self):
        ruta_csv, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecciona un CSV", ".", "Archivos CSV (*.csv)")
        if not ruta_csv:
            return

        estudiantes = cargar_estudiantes_desde_csv(ruta_csv, parent=self)
        if estudiantes is None:
            # Hubo error o campo vacío, ya se mostró mensaje en la función
            return

        # Cargar al modelo, evitando duplicados dentro de la sesión actual
        existentes = set()
        for r in range(self.model.rowCount()):
            existentes.add(self.model.item(r, 1).text().strip())

        self.model.setRowCount(0)
        for cedula, nombre in estudiantes:
            cedula = str(cedula).strip()
            nombre = str(nombre).strip()
            if not cedula or not nombre:
                continue
            if cedula in existentes:
                continue
            fila = [QStandardItem(nombre), QStandardItem(cedula)]
            for it in fila:
                it.setTextAlignment(Qt.AlignCenter)
            self.model.appendRow(fila)

    def save_students(self):
        course_index = self.selecionar_curso.currentIndex()
        course_id = self.selecionar_curso.itemData(course_index)

        if course_id is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Seleccione un curso válido")
            return

        # Validación: debe existir una lista cargada
        row_count = self.model.rowCount()
        if row_count == 0:
            QtWidgets.QMessageBox.warning(self, "Error", "No hay estudiantes cargados para guardar.")
            return

        # Validación de filas: sin celdas vacías y sin duplicados en la lista actual
        seen_ids = set()
        for row in range(row_count):
            nombre_item = self.model.item(row, 0)
            cedula_item = self.model.item(row, 1)
            nombre = nombre_item.text().strip() if nombre_item else ""
            cedula = cedula_item.text().strip() if cedula_item else ""

            if not nombre or not cedula:
                QtWidgets.QMessageBox.warning(self, "Error", f"Fila {row+1}: nombre o identificación vacíos.")
                return

            if cedula in seen_ids:
                QtWidgets.QMessageBox.warning(self, "Error", f"Identificación duplicada en la lista: {cedula}.")
                return
            seen_ids.add(cedula)

        # Persistencia
        for row in range(row_count):
            nombre = self.model.item(row, 0).text().strip()
            cedula = self.model.item(row, 1).text().strip()

            student = Student(student_id=cedula, first_name=nombre)
            student.save()

            enrollment = Enrollment(course_id=course_id, student_id=cedula)
            enrollment.save()

        QtWidgets.QMessageBox.information(self, "Guardado", "Lista de estudiantes guardada correctamente")
        self.load_courses()
