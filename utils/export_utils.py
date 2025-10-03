# utils/export_utils.py
import os
import csv
from PyQt5.QtWidgets import QFileDialog, QMessageBox

# PDF 
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def export_tableview_to_pdf(tableview, headers, parent_widget=None):
    path, _ = QFileDialog.getSaveFileName(parent_widget, "Exportar a PDF", "", "PDF Files (*.pdf)")
    if not path:
        return False

    # Forzar extensión .pdf
    base, ext = os.path.splitext(path)
    if ext.lower() != ".pdf":
        path = base + ".pdf"

    # Extraer datos
    data = [headers]
    model = tableview.model()
    for row in range(model.rowCount()):
        fila = []
        for col in range(model.columnCount()):
            item = model.item(row, col)
            fila.append(item.text() if item is not None else "")
        data.append(fila)

    # Construir PDF
    doc = SimpleDocTemplate(path, pagesize=landscape(A4))
    table = Table(data)
    style = TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.gray),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ])
    table.setStyle(style)
    doc.build([table])
    return True


def export_tableview_to_csv(tableview, headers=None, parent_widget=None, default_name="export.csv"):
    """
    Exporta el contenido visible de un QTableView a CSV con codificación UTF-8 BOM.
    - headers: lista de encabezados; si es None, toma los del modelo si existen.
    """
    path, _ = QFileDialog.getSaveFileName(
        parent_widget,
        "Exportar a CSV",
        default_name,
        "Archivos CSV (*.csv)"
    )
    if not path:
        return False

    base, ext = os.path.splitext(path)
    if ext.lower() != ".csv":
        path = base + ".csv"

    try:
        model = tableview.model()

        # Determinar encabezados
        if headers is None:
            headers = []
            for col in range(model.columnCount()):
                hdr = model.headerData(col, tableview.horizontalHeader().orientation())
                headers.append(str(hdr) if hdr is not None else f"Columna {col+1}")

        with open(path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            # Escribir encabezados
            writer.writerow(headers)

            # Escribir filas
            for row in range(model.rowCount()):
                fila = []
                for col in range(model.columnCount()):
                    item = model.item(row, col)
                    fila.append(item.text() if item is not None else "")
                writer.writerow(fila)

        QMessageBox.information(parent_widget, "Exportar", f"Archivo CSV exportado en:\n{path}")
        return True
    except Exception as e:
        QMessageBox.critical(parent_widget, "Error", f"No se pudo exportar el CSV:\n{e}")
        return False
