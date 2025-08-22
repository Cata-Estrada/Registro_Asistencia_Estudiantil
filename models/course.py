from models.database import get_connection

class Course:
    def __init__(self, course_id=None, course_name=None, course_type=None, user_id=None):
        self.course_id = course_id
        self.course_name = course_name
        self.course_type = course_type
        self.user_id = user_id

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        if self.course_id is None:
            cursor.execute(
                "INSERT INTO Curso (nombre_curso, tipo, id_usuario) VALUES (?, ?, ?)",
                (self.course_name, self.course_type, self.user_id),
            )
            self.course_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE Curso SET nombre_curso=?, tipo=?, id_usuario=? WHERE id_curso=?",
                (self.course_name, self.course_type, self.user_id, self.course_id),
            )
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_by_user(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_curso, nombre_curso, tipo, id_usuario FROM Curso WHERE id_usuario=?",
            (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Course(*row) for row in rows]

    @staticmethod
    def delete(course_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Curso WHERE id_curso=?", (course_id,))
        conn.commit()
        conn.close()