# controllers/registro_estudiantil_controller.py
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from models.course import Course
from models.student import Student
from models.enrollment import Enrollment
# Verifica el nombre correcto del módulo: csv_utils vs cvs_utils
try:
    from utils.csv_utils import cargar_estudiantes_desde_csv
except ImportError:
    from utils.cvs_utils import cargar_estudiantes_desde_csv  # fallback si tu archivo se llama así

class RegistroEstudiantilController(QtWidgets.QWidget):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi("views/registro_estudiantil.ui", self)
        self.user_id = user_id

        # Callback opcional inyectado desde el Dashboard para notificar creación de cursos
        self._curso_creado_cb = None

        # Modelo de la tabla de estudiantes
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Nombre del Estudiante", "Número de identificación"])
        self.tableView.setModel(self.model)

        # Cargar cursos al inicio
        self.load_courses()

        # Conexiones UI
        self.agregar_curso.clicked.connect(self.add_course)
        self.cargar_lista_estudiantes.clicked.connect(self.cargar_estudiantes_csv)
        self.guardar_lista_curso.clicked.connect(self.save_students)

    def set_curso_creado_callback(self, cb):
        """Inyectado por el Dashboard: cb recibe un objeto Course recién creado."""
        self._curso_creado_cb = cb

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

        nuevo_curso = Course(course_name=course_name, course_type="", user_id=self.user_id)
        nuevo_curso.save()

        # Notificar en caliente a CursoController (si está conectado)
        if self._curso_creado_cb:
            self._curso_creado_cb(nuevo_curso)

        self.nombre_curso.clear()
        self.load_courses()
        QtWidgets.QMessageBox.information(self, "Éxito", "Curso agregado correctamente")

    def cargar_estudiantes_csv(self):
        ruta_csv, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecciona un CSV", ".", "Archivos CSV (*.csv)")
        if ruta_csv:
            estudiantes = cargar_estudiantes_desde_csv(ruta_csv, parent=self)
            if estudiantes is None:
                # Hubo error o campo vacío, ya se mostró mensaje
                return
            self.model.setRowCount(0)
            for cedula, nombre in estudiantes:
                fila = [QStandardItem(nombre), QStandardItem(cedula)]
                self.model.appendRow(fila)

    def save_students(self):
        course_index = self.selecionar_curso.currentIndex()
        course_id = self.selecionar_curso.itemData(course_index)

        if course_id is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Seleccione un curso válido")
            return

        for row in range(self.model.rowCount()):
            nombre = self.model.item(row, 0).text()
            cedula = self.model.item(row, 1).text()

            student = Student(student_id=cedula, first_name=nombre)
            student.save()

            enrollment = Enrollment(course_id=course_id, student_id=cedula)
            enrollment.save()

        QtWidgets.QMessageBox.information(self, "Guardado", "Lista de estudiantes guardada correctamente")
        self.load_courses()
