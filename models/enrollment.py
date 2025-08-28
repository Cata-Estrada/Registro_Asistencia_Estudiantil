from models.database import get_connection

class Enrollment:
    def __init__(self, course_id=None, student_id=None):
        self.course_id = course_id
        self.student_id = student_id

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO Inscripcion (id_curso, cedula_estudiante) VALUES (?, ?)",
            (self.course_id, self.student_id),
        )
        conn.commit()
        conn.close()

    @staticmethod
    def get_students_by_course(course_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.cedula, e.nombre_estudiante 
            FROM Estudiante e
            INNER JOIN Inscripcion i ON e.cedula = i.cedula_estudiante
            WHERE i.id_curso = ?
        """, (course_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows  # devuelve lista de tuplas (cedula, nombre_estudiante)

    @staticmethod
    def delete(course_id, student_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Inscripcion WHERE id_curso=? AND cedula_estudiante=?",
            (course_id, student_id),
        )
        conn.commit()
        conn.close()
