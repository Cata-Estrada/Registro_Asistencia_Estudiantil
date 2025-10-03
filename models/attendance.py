# models/attendance.py
from models.database import get_connection

class Attendance:
    def __init__(self, attendance_id=None, class_id=None, student_id=None, status=None):
        self.attendance_id = attendance_id
        self.class_id = class_id
        self.student_id = student_id
        self.status = status  # 'presente', 'ausente', 'tarde'

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        if self.attendance_id is None:
            cursor.execute(
                "SELECT id_asistencia FROM Asistencia WHERE id_clase=? AND cedula_estudiante=?",
                (self.class_id, self.student_id),
            )
            row = cursor.fetchone()
            if row:
                self.attendance_id = row[0]
                cursor.execute(
                    "UPDATE Asistencia SET estado=? WHERE id_asistencia=?",
                    (self.status, self.attendance_id),
                )
            else:
                cursor.execute(
                    "INSERT INTO Asistencia (id_clase, cedula_estudiante, estado) VALUES (?, ?, ?)",
                    (self.class_id, self.student_id, self.status),
                )
                self.attendance_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE Asistencia SET id_clase=?, cedula_estudiante=?, estado=? WHERE id_asistencia=?",
                (self.class_id, self.student_id, self.status, self.attendance_id),
            )
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_class(class_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_asistencia, id_clase, cedula_estudiante, estado FROM Asistencia WHERE id_clase=?",
            (class_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [Attendance(*row) for row in rows]

    @staticmethod
    def get_historial(course_id, fecha=None, nombre_estudiante=None):
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT est.nombre_estudiante, c.fecha_clase, est.cedula, a.estado
            FROM Asistencia a
            JOIN Clase c ON a.id_clase = c.id_clase
            JOIN Estudiante est ON a.cedula_estudiante = est.cedula
            WHERE c.id_curso = ?
        """
        params = [course_id]
        if fecha:
            query += " AND c.fecha_clase = ?"
            params.append(fecha)
        if nombre_estudiante:
            query += " AND est.nombre_estudiante LIKE ?"
            params.append(f"%{nombre_estudiante}%")
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_report(course_id):
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT est.nombre_estudiante,
                   SUM(CASE WHEN a.estado='presente' THEN 1 ELSE 0 END) AS presentes,
                   SUM(CASE WHEN a.estado='tarde' THEN 1 ELSE 0 END) AS tardes,
                   SUM(CASE WHEN a.estado='ausente' THEN 1 ELSE 0 END) AS ausentes,
                   COUNT(a.id_asistencia) AS total
            FROM Asistencia a
            JOIN Clase c ON a.id_clase = c.id_clase
            JOIN Estudiante est ON a.cedula_estudiante = est.cedula
            WHERE c.id_curso = ?
            GROUP BY est.nombre_estudiante
        """
        cursor.execute(query, (course_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def delete(attendance_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Asistencia WHERE id_asistencia=?", (attendance_id,))
        conn.commit()
        conn.close()
