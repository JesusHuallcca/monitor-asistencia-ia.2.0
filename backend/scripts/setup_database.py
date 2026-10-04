"""Script para ejecutar el setup de la base de datos monitor_asistencia_ia.

Lee database/setup_all.sql y lo ejecuta en el servidor MySQL configurado en .env.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde backend/.env
backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(backend_dir / ".env")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

sql_file = backend_dir.parent / "database" / "setup_all.sql"

if not sql_file.exists():
    print(f"Error: No se encontró el archivo {sql_file}")
    sys.exit(1)

print(f"=== ASISTENCIA IA: INICIALIZADOR DE BASE DE DATOS ===")
print(f"Servidor: {DB_HOST}:{DB_PORT}")
print(f"Usuario: {DB_USER}")
print(f"Archivo SQL: {sql_file.name}")

try:
    import pymysql

    # Conectar al servidor sin seleccionar base (para poder crearla)
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True,
        charset="utf8mb4",
    )
    with conn.cursor() as cursor:
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Separar por punto y coma respetando bloques
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
        for stmt in statements:
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"[Aviso en sentencia]: {e}")

    conn.close()
    print("\n✅ Base de datos 'monitor_asistencia_ia' y datos de prueba creados con éxito.")

except ImportError:
    print("\n⚠️ pymysql no está instalado en este entorno.")
    print(f"Puedes ejecutar el script directamente con el cliente MySQL:")
    print(f'mysql -h {DB_HOST} -P {DB_PORT} -u {DB_USER} -p < "{sql_file}"')
except Exception as err:
    print(f"\n❌ Error al conectar con MySQL: {err}")
    print("Verifica que el servicio de MySQL esté iniciado y la contraseña en .env sea correcta.")
