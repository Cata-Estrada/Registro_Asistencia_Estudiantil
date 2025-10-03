from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView, QStyledItemDelegate
from PyQt5.QtCore import Qt
from models.course import Course
from models.attendance import Attendance
from utils.export_utils import export_tableview_to_pdf
from utils.paths import rel_path 

class CenterAlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter


class ReportesController(QtWidgets.QWidget):
    def __init__(self, user_id):
        super().__init__()
        uic.loadUi(rel_path("views", "reporte.ui"), self)
        self.user_id = user_id
        self.headers = [
            "Nombre Estudiante", "Presente", "Tarde", "Ausente",
            "%Presente", "%Tarde", "%Ausente"
        ]
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.headers)
        self.tableView.setModel(self.model)

        # Centrar celdas
        self._center_delegate = CenterAlignDelegate(self.tableView)
        self.tableView.setItemDelegate(self._center_delegate)

        # Configurar columnas proporcionales y encabezados centrados
        self._configure_table_columns()

        self.load_courses()
        self.selecione_curso.currentIndexChanged.connect(self.clear_report)
        self.generar_reporte.clicked.connect(self.load_report)
        self.exportar_reporte.clicked.connect(self.export_report)

    def _configure_table_columns(self):
        self.tableView.horizontalHeader().setVisible(True)
        self.tableView.verticalHeader().setVisible(False)

        hh = self.tableView.horizontalHeader()
        try:
            hh.setDefaultAlignment(Qt.AlignCenter)
        except AttributeError:
            pass

        # Proporcionalidad: todas las columnas en Stretch
        hh.setStretchLastSection(False)
        for col in range(7):
            hh.setSectionResizeMode(col, QHeaderView.Stretch)

        # Mínimos razonables por tipo de dato
        self.tableView.horizontalHeader().setMinimumSectionSize(110)
        self.tableView.setColumnWidth(0, 240)  # Nombre Estudiante un poco más ancho
        for col in range(1, 7):
            self.tableView.setColumnWidth(col, 120)

        # Selección y filas
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.verticalHeader().setDefaultSectionSize(28)
        self.tableView.setTextElideMode(Qt.ElideNone)

    def load_courses(self):
        self.selecione_curso.clear()
        self.selecione_curso.addItem("Seleccione curso", None)
        self.selecione_curso.model().item(0).setEnabled(False)

        courses = Course.get_all_by_user(user_id=self.user_id)
        for c in courses:
            self.selecione_curso.addItem(c.course_name, c.course_id)

        self.selecione_curso.setCurrentIndex(0)

    def clear_report(self):
        """Limpia la tabla siempre que cambie el curso"""
        self.model.setRowCount(0)

    def load_report(self):
        """Genera el reporte del curso seleccionado"""
        self.model.setRowCount(0)
        course_id = self.selecione_curso.itemData(self.selecione_curso.currentIndex())

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
            for it in fila:
                it.setTextAlignment(Qt.AlignCenter)
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
