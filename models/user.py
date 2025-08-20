from models.database import get_connection


class User:
    def __init__(self, user_id=None, username=None, correo=None, password=None):
        self.user_id = user_id
        self.username = username
        self.correo = correo
        self.password = password

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        if self.user_id is None:
            cursor.execute(
                "INSERT INTO Usuario (nombre_usuario, correo, contraseña) VALUES (?, ?, ?)",
                (self.username, self.correo, self.password),
            )
            self.user_id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE Usuario SET nombre_usuario=?, correo=?, contraseña=? WHERE id_usuario=?",
                (self.username, self.correo, self.password, self.user_id),
            )
        conn.commit()
        conn.close()

    @staticmethod
    def find_by_username_or_email(identifier):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_usuario, nombre_usuario, correo, contraseña FROM Usuario WHERE nombre_usuario=? OR correo=?",
            (identifier, identifier),
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(*row)
        return None
    
    @staticmethod
    def delete(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Usuario WHERE id_usuario=?", (user_id,))
        conn.commit()
        conn.close()