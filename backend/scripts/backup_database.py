"""
Script de Respaldo y Mantenimiento de Base de Datos MySQL
Genera copias de seguridad de la BD `monitor_asistencia_ia` en formato SQL / JSON.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE_DIR / "backups"

def run_backup():
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = BACKUP_DIR / f"backup_monitor_asistencia_{timestamp}.sql"
    
    print(f"[+] Iniciando respaldo de MySQL en: {filename}")
    
    db_user = os.getenv("DB_USER", "root")
    db_pass = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "monitor_asistencia_ia")
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "3306")

    # Intentar mysqldump
    cmd = [
        "mysqldump",
        f"--host={db_host}",
        f"--port={db_port}",
        f"--user={db_user}",
        f"--result-file={filename}",
        db_name
    ]
    if db_pass:
        cmd.append(f"--password={db_pass}")

    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"[OK] Respaldo SQL generado exitosamente ({filename.stat().st_size} bytes)")
            return True
        else:
            print(f"[!] mysqldump no disponible en PATH o fallo de credenciales: {res.stderr}")
    except Exception as e:
        print(f"[!] Error ejecutando mysqldump: {e}")

    # Fallback: Respaldo JSON directo usando SQLAlchemy
    print("[+] Ejecutando respaldo secundario via SQLAlchemy / JSON Export...")
    try:
        sys.path.insert(0, str(BASE_DIR))
        from app.core.database import SessionLocal
        from app.models import Usuario, Estudiante, Profesor, Curso, Asistencia, Auditoria
        
        db = SessionLocal()
        json_filename = BACKUP_DIR / f"backup_dump_{timestamp}.json"
        
        data = {
            "timestamp": timestamp,
            "usuarios": [
                {"id": u.id_usuario, "correo": u.correo, "rol": u.rol, "nombres": u.nombres}
                for u in db.query(Usuario).all()
            ],
            "cursos": [
                {"id": c.id_curso, "codigo": c.codigo, "nombre": c.nombre}
                for c in db.query(Curso).all()
            ],
            "asistencias_count": db.query(Asistencia).count(),
            "auditoria_count": db.query(Auditoria).count(),
        }
        
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        print(f"[OK] Respaldo JSON de emergencia completado en: {json_filename}")
        return True
    except Exception as ex:
        print(f"[ERROR] Fallo total en respaldo de base de datos: {ex}")
        return False

if __name__ == "__main__":
    run_backup()
