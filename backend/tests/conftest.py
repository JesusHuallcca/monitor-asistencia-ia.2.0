"""
Fixtures y configuración global para suite de pruebas Pytest.
Fase 8: Hardening y Calidad.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from app.core.database import SessionLocal
from app.models import Usuario


@pytest.fixture(scope="session")
def client():
    """Cliente HTTP de prueba para FastAPI."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def admin_token():
    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.rol == "ADMINISTRADOR").first()
    uid = str(user.id_usuario) if user else "1"
    db.close()
    return create_access_token({"sub": uid, "rol": "ADMINISTRADOR"})


@pytest.fixture(scope="session")
def profesor_token():
    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.rol == "PROFESOR").first()
    uid = str(user.id_usuario) if user else "2"
    db.close()
    return create_access_token({"sub": uid, "rol": "PROFESOR"})


@pytest.fixture(scope="session")
def estudiante_token():
    db = SessionLocal()
    user = db.query(Usuario).filter(Usuario.rol == "ESTUDIANTE").first()
    uid = str(user.id_usuario) if user else "3"
    db.close()
    return create_access_token({"sub": uid, "rol": "ESTUDIANTE"})


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def profesor_headers(profesor_token):
    return {"Authorization": f"Bearer {profesor_token}"}


@pytest.fixture(scope="session")
def estudiante_headers(estudiante_token):
    return {"Authorization": f"Bearer {estudiante_token}"}
