import csv
from PyQt5.QtWidgets import QMessageBox

def cargar_estudiantes_desde_csv(path, parent=None):
    estudiantes = []
    try:
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Comprobar que campos obligatorios estén en el archivo
            required_fields = ['cedula', 'nombre_estudiante']
            for field in required_fields:
                if field not in reader.fieldnames:
                    if parent:
                        QMessageBox.warning(parent, "Error", f"El archivo CSV no contiene el campo '{field}'")
                    return None

            for i, row in enumerate(reader, start=1):
                cedula = row.get('cedula', '').strip()
                nombre = row.get('nombre_estudiante', '').strip()

                if not cedula or not nombre:
                    if parent:
                        QMessageBox.warning(parent, "Error", f"El archivo tiene campos vacíos en fila {i}")
                    return None

                # Solo almacenar cédula y nombre, ignorando otras columnas
                estudiantes.append((cedula, nombre))

    except Exception as e:
        if parent:
            QMessageBox.warning(parent, "Error", f"No se pudo leer el archivo CSV:\n{e}")
        return None

    return estudiantes