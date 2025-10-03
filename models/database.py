# models/database.py
import sqlite3
from utils.paths import db_path, seed_db_from_project

def get_connection():
    # Asegura que exista una BD en la carpeta de datos de usuario
    seed_db_from_project()
    return sqlite3.connect(db_path())

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS Usuario (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_usuario TEXT NOT NULL UNIQUE,
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
