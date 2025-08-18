import sqlite3
import os

# Carpeta raíz del proyecto, un nivel arriba de 'models'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, 'asistencia.db')

def get_connection():
    # Aquí se conecta o crea la base dentro de la carpeta de proyecto
    return sqlite3.connect(DB_NAME)

def create_tables():
    # Crea las tablas del esquema
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Usuario (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_usuario TEXT NOT NULL,
        correo TEXT NOT NULL UNIQUE,
        contraseña TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS Curso (
        id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_curso TEXT NOT NULL,
        tipo TEXT,
        id_usuario INTEGER NOT NULL,
        FOREIGN KEY(id_usuario) REFERENCES Usuario(id_usuario)
    );
    CREATE TABLE IF NOT EXISTS Estudiante (
        cedula TEXT PRIMARY KEY,
        nombre_estudiante TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS Inscripcion (
        id_curso INTEGER NOT NULL,
        cedula_estudiante TEXT NOT NULL,
        PRIMARY KEY(id_curso, cedula_estudiante),
        FOREIGN KEY(id_curso) REFERENCES Curso(id_curso),
        FOREIGN KEY(cedula_estudiante) REFERENCES Estudiante(cedula)
    );
    CREATE TABLE IF NOT EXISTS Clase (
        id_clase INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_clase TEXT NOT NULL,
        id_curso INTEGER NOT NULL,
        FOREIGN KEY(id_curso) REFERENCES Curso(id_curso)
    );
    CREATE TABLE IF NOT EXISTS Asistencia (
        id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_clase INTEGER NOT NULL,
        cedula_estudiante TEXT NOT NULL,
        estado TEXT NOT NULL CHECK(estado IN ('presente', 'ausente', 'tarde')),
        FOREIGN KEY(id_clase) REFERENCES Clase(id_clase),
        FOREIGN KEY(cedula_estudiante) REFERENCES Estudiante(cedula)
    );
    """)
    conn.commit()
    conn.close()
    print(f"Base de datos creada o actualizada en: {DB_NAME}")

if __name__ == "__main__":
    create_tables()
