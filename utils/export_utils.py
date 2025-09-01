from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from PyQt5.QtWidgets import QFileDialog

def export_tableview_to_pdf(tableview, headers, parent_widget=None):
    path, _ = QFileDialog.getSaveFileName(parent_widget, "Exportar a PDF", "", "PDF Files (*.pdf)")
    if not path:
        return False

    doc = SimpleDocTemplate(path, pagesize=landscape(A4))
    data = [headers]
    
    # Extraer los datos de la tabla
    model = tableview.model()
    for row in range(model.rowCount()):
        fila = []
        for col in range(model.columnCount()):
            item = model.item(row, col)
            fila.append(item.text() if item is not None else "")
        data.append(fila)

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
    elements = [table]
    doc.build(elements)
    return True
    