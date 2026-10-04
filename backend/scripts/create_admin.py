"""Script para crear el primer administrador con hash bcrypt seguro."""

import os
import sys
from pathlib import Path

# Añadir el directorio raíz del backend al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.core.database import engine, SessionLocal
from app.models import Usuario, Base
from app.core.security import hash_password


def create_admin(
    nombres: str = "Administrador",
    apellidos: str = "Principal",
    correo: str = "admin@asistencia.local",
    password: str = "Admin2026!",
):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(Usuario).filter(Usuario.correo == correo).first()
        if existing:
            print(f"⚠️  Ya existe un usuario con correo '{correo}' (rol: {existing.rol}).")
            return

        admin = Usuario(
            nombres=nombres,
            apellidos=apellidos,
            correo=correo,
            password_hash=hash_password(password),
            rol="ADMINISTRADOR",
            estado=True,
        )
        db.add(admin)
        db.commit()
        print(f"✅ Administrador creado exitosamente:")
        print(f"   Correo:     {correo}")
        print(f"   Contraseña: {password}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
