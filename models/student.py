from models.database import get_connection

class Student:
    def __init__(self, student_id=None, first_name=None):
        self.student_id = student_id  # corresponde a cedula en la base
        self.first_name = first_name  # corresponde a nombre_estudiante en la base

    @staticmethod
    def find_by_id(student_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT cedula, nombre_estudiante FROM Estudiante WHERE cedula=?", (student_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return Student(*row)
        return None

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        if self.find_by_id(self.student_id) is None:
            cursor.execute(
                "INSERT INTO Estudiante (cedula, nombre_estudiante) VALUES (?, ?)",
                (self.student_id, self.first_name),
            )
        else:
            cursor.execute(
                "UPDATE Estudiante SET nombre_estudiante=? WHERE cedula=?",
                (self.first_name, self.student_id),
            )
        conn.commit()
        conn.close()

    

    @staticmethod
    def delete(student_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Estudiante WHERE cedula=?", (student_id,))
        conn.commit()
        conn.close()
