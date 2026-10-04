# Persona 1 (Jhoshef): lectura/actualización de perfil y cambio de contraseña
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.models import Usuario
from app.schemas.perfil import PerfilActualizar, PerfilOut
from app.services.auth_service import registrar_auditoria


def armar_perfil(user: Usuario) -> PerfilOut:
    rostro = getattr(user, "rostro", None)
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "nombres": user.nombres,
        "apellidos": user.apellidos,
        "rol": user.rol,
        "estado": user.estado,
        "tiene_login_facial": bool(
            rostro
            and getattr(rostro, "consentimiento", False)
            and getattr(rostro, "login_facial_activo", False)
        ),
        "codigo": None,
        "carrera": None,
        "ciclo": None,
        "especialidad": None,
        "telefono": None,
    }
    if user.estudiante is not None:
        est = user.estudiante
        data["codigo"] = getattr(est, "codigo", None)
        data["carrera"] = getattr(est, "carrera", None)
        data["ciclo"] = getattr(est, "ciclo", None)
    if user.profesor is not None:
        prof = user.profesor
        data["especialidad"] = getattr(prof, "especialidad", None)
        data["telefono"] = getattr(prof, "telefono", None)
    return PerfilOut(**data)


def actualizar_perfil(db: Session, user: Usuario, datos: PerfilActualizar, ip: str | None = None) -> PerfilOut:
    if datos.nombres is not None:
        user.nombres = datos.nombres.strip()
    if datos.apellidos is not None:
        user.apellidos = datos.apellidos.strip()
    if datos.email is not None:
        email = str(datos.email).strip().lower()
        otro = db.query(Usuario).filter(Usuario.email == email, Usuario.id != user.id).first()
        if otro:
            raise HTTPException(status_code=400, detail="El correo ya está en uso")
        user.email = email

    if user.profesor is not None:
        if datos.especialidad is not None:
            user.profesor.especialidad = datos.especialidad.strip() or None
        if datos.telefono is not None:
            user.profesor.telefono = datos.telefono.strip() or None

    if user.estudiante is not None:
        if datos.carrera is not None:
            user.estudiante.carrera = datos.carrera.strip() or None
        if datos.ciclo is not None:
            user.estudiante.ciclo = datos.ciclo

    db.add(user)
    db.commit()
    db.refresh(user)
    try:
        registrar_auditoria(db, user.id, "perfil_actualizar", ip=ip)
    except Exception:
        pass
    return armar_perfil(user)


def cambiar_password(db: Session, user: Usuario, actual: str, nueva: str, ip: str | None = None) -> None:
    if not verify_password(actual, user.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta")
    if len(nueva) < 8:
        raise HTTPException(status_code=400, detail="La nueva contraseña debe tener al menos 8 caracteres")
    user.password_hash = hash_password(nueva)
    db.add(user)
    db.commit()
    try:
        registrar_auditoria(db, user.id, "password_cambiar", ip=ip)
    except Exception:
        pass