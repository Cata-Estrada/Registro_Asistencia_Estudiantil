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