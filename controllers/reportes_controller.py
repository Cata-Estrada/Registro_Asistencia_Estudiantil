from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from models.course import Course
from models.attendance import Attendance
from utils.export_utils import export_tableview_to_pdf

class ReportesController(QtWidgets.QWidget):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi("views/reporte.ui", self)
        self.user_id = user_id
        self.headers = [
            "Nombre Estudiante", "Presente", "Tarde", "Ausente",
            "%Presente", "%Tarde", "%Ausente"
        ]
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.headers)
        self.tableView.setModel(self.model)
        self.load_courses()
        self.selecione_curso.currentIndexChanged.connect(self.clear_report)
        self.generar_reporte.clicked.connect(self.load_report)
        self.exportar_reporte.clicked.connect(self.export_report)

    def load_courses(self):
        self.selecione_curso.clear()

        # Agregar un item falso como placeholder
        self.selecione_curso.addItem("Seleccione curso", None)
        self.selecione_curso.model().item(0).setEnabled(False)

        #Cargar cursos del usuario
        courses = Course.get_all_by_user(user_id=self.user_id)
        for c in courses:
            self.selecione_curso.addItem(c.course_name, c.course_id)

        # Asegurar que quede en el placeholder al cargar
        self.selecione_curso.setCurrentIndex(0)

    def clear_report(self):
        """Limpia la tabla siempre que cambie el curso"""
        self.model.setRowCount(0)

    def load_report(self):
        """Genera el reporte del curso seleccionado"""
        self.model.setRowCount(0)
        course_id = self.selecione_curso.itemData(self.selecione_curso.currentIndex())

        # Si está en el placeholder, no hacer nada
        if course_id is None:
            return

        rows = Attendance.get_report(course_id)
        for r in rows:
            nombre, presentes, tardes, ausentes, total = r
            pc_presente = f"{(presentes * 100 // total) if total else 0}%"
            pc_tarde = f"{(tardes * 100 // total) if total else 0}%"
            pc_ausente = f"{(ausentes * 100 // total) if total else 0}%"
            fila = [
                QStandardItem(nombre),
                QStandardItem(str(presentes)),
                QStandardItem(str(tardes)),
                QStandardItem(str(ausentes)),
                QStandardItem(pc_presente),
                QStandardItem(pc_tarde),
                QStandardItem(pc_ausente)
            ]
            self.model.appendRow(fila)

    def export_report(self):
        """Exporta el reporte actual a PDF"""
        if self.model.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self, "Advertencia", "No hay reporte para exportar.")
            return
        ok = export_tableview_to_pdf(self.tableView, self.headers, self)
        if ok:
            QtWidgets.QMessageBox.information(self, "Exportar", "Reporte exportado correctamente")
        else:
            QtWidgets.QMessageBox.information(self, "Exportar", "No se exportó el PDF")
