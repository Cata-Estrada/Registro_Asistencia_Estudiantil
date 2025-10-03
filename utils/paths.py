# utils/paths.py
import sys, os
from pathlib import Path

def base_path():
    if hasattr(sys, "frozen") and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # raíz del proyecto

def rel_path(*parts):
    return os.path.join(base_path(), *parts)

def user_data_dir(app_name="RegistroAsistencia"):
    base = Path(os.getenv("APPDATA") or base_path())  # Windows: %APPDATA%
    p = base / app_name
    p.mkdir(parents=True, exist_ok=True)
    return str(p)

def db_path(filename="asistencia.db"):
    return os.path.join(user_data_dir(), filename)

def seed_db_from_project():
    """Copia una BD inicial de la raíz del proyecto a la carpeta de usuario si no existe aún."""
    src = rel_path("asistencia.db")
    dst = db_path()
    if os.path.exists(src) and not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        import shutil; shutil.copy2(src, dst)
