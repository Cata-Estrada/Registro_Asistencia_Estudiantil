from models.database import get_connection

class ClassSession:
    def __init__(self, class_id=None, class_date=None, course_id=None):
        self.class_id = class_id
        self.class_date = class_date
        self.course_id = course_id

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        if self.class_id is None:
            cursor.execute(
                "INSERT INTO Clase (fecha_clase, id_curso) VALUES (?, ?)",
                (self.class_date, self.course_id),
            )
            self.class_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE Clase SET fecha_clase=?, id_curso=? WHERE id_clase=?",
                (self.class_date, self.course_id, self.class_id),
            )
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_date_and_course(class_date, course_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_clase, fecha_clase, id_curso FROM Clase WHERE fecha_clase=? AND id_curso=?",
            (class_date, course_id),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return ClassSession(*row)
        return None