# controllers/curso_controller.py
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QHeaderView
from models.course import Course


class CursoController(QtWidgets.QWidget):
    curso_seleccionado_changed = QtCore.pyqtSignal(object)  # Emite el Course seleccionado o None

    def __init__(self, user_id: int):
        super().__init__()
        uic.loadUi("views/curso.ui", self)

        # Estado
        self.user_id = user_id
        self.curso_actual_id = None  # id_curso actualmente en edición (None = crear)
        self.tipo_por_defecto = "regular"  # Ajusta si tu dominio usa otro valor

        # Modelo de tabla con proxy para ordenar/filtrar
        # Mantenemos 3 columnas (ID, Nombre, Tipo) para la lógica interna,
        # pero solo se mostrará la columna "Nombre".
        self.model = QStandardItemModel(0, 3, self)
        self.model.setHorizontalHeaderLabels(["ID", "Nombre", "Tipo"])
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setFilterKeyColumn(1)  # filtra por "Nombre"

        # Configurar QTableView
        self.lista_cursos.setModel(self.proxy)
        self.lista_cursos.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.lista_cursos.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.lista_cursos.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # Encabezados centrados y columnas proporcionales
        hh = self.lista_cursos.horizontalHeader()
        try:
            hh.setDefaultAlignment(Qt.AlignCenter)
        except AttributeError:
            pass

        hh.setStretchLastSection(False)
        # Aunque solo se muestre "Nombre", aplicamos Stretch a todas para proporcionalidad
        hh.setSectionResizeMode(0, QHeaderView.Stretch)  # ID (oculta)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)  # Nombre (visible)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)  # Tipo (oculta)
        hh.setMinimumSectionSize(140)

        # Mostrar solo "Nombre": ocultar ID (col 0) y Tipo (col 2)
        self.lista_cursos.setColumnHidden(0, True)  # ID oculto
        self.lista_cursos.setColumnHidden(2, True)  # Tipo oculto

        # Centrar contenido
        self.lista_cursos.setTextElideMode(Qt.ElideNone)

        # Conexiones UI
        self.agregar_curso.clicked.connect(self.on_guardar)       # Guardar (crear/actualizar)
        self.actualizar_curso.clicked.connect(self.on_preparar_actualizar)  # Cargar selección al formulario
        self.eliminar_curso.clicked.connect(self.on_eliminar)     # Eliminar seleccionado
        self.buscar_curso.clicked.connect(self.on_buscar)         # Filtrar por nombre
        self.lineEdit_2.returnPressed.connect(self.on_buscar)
        self.lista_cursos.selectionModel().selectionChanged.connect(self.on_cambio_seleccion)

        # Cargar datos iniciales
        self.load_courses()

    # --------- Operaciones principales ----------
    def load_courses(self):
        """Carga todos los cursos del usuario y refresca la tabla."""
        self.model.removeRows(0, self.model.rowCount())
        cursos = Course.get_all_by_user(self.user_id)
        for c in cursos:
            self._agregar_fila(c)
        # Limpiar selección y formulario
        self.lista_cursos.clearSelection()
        self._limpiar_formulario()
        self.curso_seleccionado_changed.emit(None)

    def on_guardar(self):
        """Crea o actualiza un curso según curso_actual_id."""
        nombre = self.lineEdit.text().strip()
        if not nombre:
            QtWidgets.QMessageBox.warning(self, "Validación", "El nombre del curso es obligatorio.")
            return

        tipo = self.tipo_por_defecto  # No hay campo tipo en UI

        if self.curso_actual_id is None:
            # Crear
            curso = Course(course_name=nombre, course_type=tipo, user_id=self.user_id)
            curso.save()
            self._agregar_fila(curso)
            QtWidgets.QMessageBox.information(self, "Éxito", "Curso creado correctamente.")
        else:
            # Actualizar
            curso = Course(course_id=self.curso_actual_id, course_name=nombre, course_type=tipo, user_id=self.user_id)
            curso.save()
            self._actualizar_fila(curso)
            QtWidgets.QMessageBox.information(self, "Éxito", "Curso actualizado correctamente.")

        self._limpiar_formulario()

    def on_preparar_actualizar(self):
        """Pasa la fila seleccionada al formulario para editar."""
        curso = self._curso_seleccionado()
        if not curso:
            QtWidgets.QMessageBox.information(self, "Información", "Selecciona un curso para actualizar.")
            return
        self.curso_actual_id = curso.course_id
        self.lineEdit.setText(curso.course_name)

    def on_eliminar(self):
        """Elimina el curso seleccionado."""
        curso = self._curso_seleccionado()
        if not curso:
            QtWidgets.QMessageBox.information(self, "Información", "Selecciona un curso para eliminar.")
            return

        resp = QtWidgets.QMessageBox.question(
            self, "Confirmar", f"¿Eliminar el curso '{curso.course_name}'?"
        )
        if resp != QtWidgets.QMessageBox.Yes:
            return

        Course.delete(curso.course_id)
        self._eliminar_fila_por_id(curso.course_id)
        self._limpiar_formulario()
        QtWidgets.QMessageBox.information(self, "Éxito", "Curso eliminado.")

    def on_buscar(self):
        """Filtra por nombre usando lineEdit_2."""
        criterio = self.lineEdit_2.text().strip()
        self.proxy.setFilterFixedString(criterio)

    # --------- Utilitarios de tabla/form ----------
    def _agregar_fila(self, curso: Course):
        row = [
            QStandardItem(str(curso.course_id)),
            QStandardItem(curso.course_name or ""),
            QStandardItem(curso.course_type or ""),
        ]
        for it in row:
            it.setEditable(False)
            it.setTextAlignment(Qt.AlignCenter)
        self.model.appendRow(row)

    def _actualizar_fila(self, curso: Course):
        """Encuentra la fila por ID y actualiza sus valores."""
        for r in range(self.model.rowCount()):
            id_item = self.model.item(r, 0)
            if id_item and id_item.text() == str(curso.course_id):
                self.model.setItem(r, 1, QStandardItem(curso.course_name or ""))
                self.model.setItem(r, 2, QStandardItem(curso.course_type or ""))
                self.model.item(r, 1).setEditable(False)
                self.model.item(r, 2).setEditable(False)
                self.model.item(r, 1).setTextAlignment(Qt.AlignCenter)
                self.model.item(r, 2).setTextAlignment(Qt.AlignCenter)
                return

    def _eliminar_fila_por_id(self, course_id: int):
        for r in range(self.model.rowCount()):
            if self.model.item(r, 0).text() == str(course_id):
                self.model.removeRow(r)
                return

    def _curso_seleccionado(self):
        """Devuelve un Course de la fila seleccionada (o None)."""
        sel = self.lista_cursos.selectionModel().selectedRows()
        if not sel:
            return None
        proxy_index = sel[0]
        src_index = self.proxy.mapToSource(proxy_index)
        row = src_index.row()
        id_curso = int(self.model.item(row, 0).text())
        nombre = self.model.item(row, 1).text()
        tipo = self.model.item(row, 2).text()
        return Course(course_id=id_curso, course_name=nombre, course_type=tipo, user_id=self.user_id)

    def _limpiar_formulario(self):
        self.curso_actual_id = None
        self.lineEdit.clear()

    def on_cambio_seleccion(self):
        """Emite señal con Course seleccionado o None y no toca el formulario."""
        curso = self._curso_seleccionado()
        self.curso_seleccionado_changed.emit(curso)

    # --------- Sincronización externa ----------
    def on_curso_creado_externo(self, curso: Course):
        """Añade a la tabla un curso creado desde otro controlador en caliente."""
        # Evitar duplicados por ID
        for r in range(self.model.rowCount()):
            if self.model.item(r, 0).text() == str(curso.course_id):
                return
        # Agregar la fila nueva (ID y Tipo quedan ocultos en la vista)
        row = [
            QStandardItem(str(curso.course_id)),
            QStandardItem(curso.course_name or ""),
            QStandardItem(curso.course_type or ""),
        ]
        for it in row:
            it.setEditable(False)
            it.setTextAlignment(Qt.AlignCenter)
        self.model.appendRow(row)
