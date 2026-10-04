import os
import sys
sys.path.append(os.path.abspath('backend'))  # add project root for imports
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, engine, get_db
from app.models.user import User
import bcrypt

# Cargar variables de entorno (asegúrate de que .env esté configurado)
from dotenv import load_dotenv
load_dotenv()

# Reutilizar motor y sesión definidos en database.py
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_user(username: str, password: str, email: str, role: str, full_name: str = ""):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(
        username=username,
        password_hash=hashed,
        role=role,
        full_name=full_name,
        email=email,
    )
    return user

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Profesor
        if not db.query(User).filter(User.username == "teacher1").first():
            db.add(create_user("teacher1", "teacher123", "teacher1@example.com", "teacher", "Profesor de Prueba"))
        # DMI (asumimos rol "teacher" también, pero puedes cambiar)
        if not db.query(User).filter(User.username == "dmi_user").first():
            db.add(create_user("dmi_user", "dmi123", "dmi@example.com", "teacher", "DMI Usuario"))
        db.commit()
        print("Usuarios de prueba creados/actualizados.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
