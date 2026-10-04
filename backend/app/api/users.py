"""Gestión de usuarios por rol (Fase 3).

Reglas:
  ADMINISTRADOR → puede crear PROFESOR y ESTUDIANTE
  PROFESOR      → solo puede crear ESTUDIANTE
  ESTUDIANTE    → 403 Forbidden
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import hash_password
from app.core.auth_dependencies import CurrentUser, get_current_user
from app.models import Usuario, Estudiante, Profesor

router = APIRouter(prefix="/api/users", tags=["Usuarios"])


# ─── Schemas ──────────────────────────────────────────────────────────────────
class CreateUserRequest(BaseModel):
    nombres: str
    apellidos: str
    correo: EmailStr
    password: str
    rol: str  # ESTUDIANTE | PROFESOR
    # Datos específicos de estudiante
    codigo_estudiante: str | None = None
    carrera: str | None = None
    ciclo: str | None = None
    # Datos específicos de profesor
    codigo_profesor: str | None = None
    especialidad: str | None = None


# ─── Helper ───────────────────────────────────────────────────────────────────
def _create_usuario(db: Session, payload: CreateUserRequest) -> Usuario:
    if db.query(Usuario).filter(Usuario.correo == payload.correo).first():
        raise HTTPException(400, detail="Ya existe una cuenta con ese correo.")

    user = Usuario(
        nombres=payload.nombres.strip(),
        apellidos=payload.apellidos.strip(),
        correo=payload.correo,
        password_hash=hash_password(payload.password),
        rol=payload.rol,
        estado=True,
    )
    db.add(user)
    db.flush()  # para obtener id_usuario antes del commit

    if payload.rol == "ESTUDIANTE":
        if not payload.codigo_estudiante:
            raise HTTPException(422, detail="Se requiere código de estudiante.")
        db.add(Estudiante(
            id_usuario=user.id_usuario,
            codigo_estudiante=payload.codigo_estudiante,
            carrera=payload.carrera,
            ciclo=payload.ciclo,
        ))
    elif payload.rol == "PROFESOR":
        if not payload.codigo_profesor:
            raise HTTPException(422, detail="Se requiere código de profesor.")
        db.add(Profesor(
            id_usuario=user.id_usuario,
            codigo_profesor=payload.codigo_profesor,
            especialidad=payload.especialidad,
        ))

    db.commit()
    db.refresh(user)
    return user


# ─── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/create", status_code=201)
def create_user(
    payload: CreateUserRequest,
    current: CurrentUser,
    db: Session = Depends(get_db),
):
    if current.rol == "ESTUDIANTE":
        raise HTTPException(403, detail="Los estudiantes no pueden crear cuentas.")
    if current.rol == "PROFESOR" and payload.rol != "ESTUDIANTE":
        raise HTTPException(403, detail="El profesor solo puede crear cuentas de estudiante.")

    user = _create_usuario(db, payload)
    return {"message": "Usuario creado exitosamente.", "id_usuario": user.id_usuario, "rol": user.rol}


@router.get("/list")
def list_users(current: CurrentUser, db: Session = Depends(get_db)):
    if current.rol == "ADMINISTRADOR":
        users = db.query(Usuario).filter(Usuario.estado == True).all()
    elif current.rol == "PROFESOR":
        # Solo estudiantes matriculados en sus cursos
        prof = current.profesor
        if not prof:
            return []
        curso_ids = [c.id_curso for c in prof.cursos]
        from app.models import Matricula
        matriculas = db.query(Matricula).filter(Matricula.id_curso.in_(curso_ids)).all()
        est_ids = {m.id_estudiante for m in matriculas}
        estudiantes = db.query(Estudiante).filter(Estudiante.id_estudiante.in_(est_ids)).all()
        return [
            {"id_usuario": e.usuario.id_usuario, "nombres": e.usuario.nombres,
             "apellidos": e.usuario.apellidos, "correo": e.usuario.correo,
             "codigo_estudiante": e.codigo_estudiante, "carrera": e.carrera}
            for e in estudiantes
        ]
    else:
        raise HTTPException(403, detail="No autorizado.")

    return [
        {"id_usuario": u.id_usuario, "nombres": u.nombres, "apellidos": u.apellidos,
         "correo": u.correo, "rol": u.rol, "estado": u.estado}
        for u in users
    ]
