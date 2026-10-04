import sys, os
sys.path.append(os.path.abspath('backend'))  # add project root to PYTHONPATH

from app.core.database import Base, engine
from app.models.user import User
from sqlalchemy.orm import sessionmaker
import bcrypt

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == 'admin').first():
            print('Admin already exists')
            return
        pwd = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
        admin = User(
            username='admin',
            password_hash=pwd,
            role='admin',
            full_name='Administrador de Prueba',
            email='admin@example.com',
        )
        db.add(admin)
        db.commit()
        print('Admin user created')
    finally:
        db.close()

if __name__ == '__main__':
    # Asegurarse de que las tablas existan
    Base.metadata.create_all(bind=engine)
    create_admin()
