"""Endpoint de autenticación MySQL (Fase 3).

POST /api/auth/login  → valida credenciales, emite JWT.
GET  /api/auth/me     → retorna el perfil del usuario autenticado.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.auth_dependencies import CurrentUser, get_current_user
from app.models import Usuario, Estudiante, Profesor

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


# ─── Schemas locales ──────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    correo: str | None = None
    email: str | None = None
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombres: str
    apellidos: str
    id_usuario: int


# ─── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    correo_real = payload.correo or payload.email
    if not correo_real:
        raise HTTPException(
            status_code=422,
            detail="Debe proveer un correo o email."
        )

    user = (
        db.query(Usuario)
        .filter(Usuario.correo == correo_real, Usuario.estado == True)
        .first()
    )
    from app.core.audit import log_audit_event

    client_ip = request.client.host if request.client else "unknown"

    if not user or not verify_password(payload.password, user.password_hash):
        log_audit_event(
            db=db,
            user_id=user.id_usuario if user else None,
            accion="LOGIN_FALLIDO",
            entidad="usuarios",
            entidad_id=str(user.id_usuario) if user else None,
            detalle={"correo_intentado": correo_real, "motivo": "Credenciales invalidas"},
            ip_origen=client_ip,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )

    token = create_access_token({"sub": str(user.id_usuario), "rol": user.rol})

    log_audit_event(
        db=db,
        user_id=user.id_usuario,
        accion="LOGIN_EXITOSO",
        entidad="usuarios",
        entidad_id=str(user.id_usuario),
        detalle={"rol": user.rol, "correo": user.correo},
        ip_origen=client_ip,
    )

    return LoginResponse(
        access_token=token,
        rol=user.rol,
        nombres=user.nombres,
        apellidos=user.apellidos,
        id_usuario=user.id_usuario,
    )


@router.get("/me")
def me(current: CurrentUser):
    extra = {}
    if current.estudiante:
        extra = {
            "codigo_estudiante": current.estudiante.codigo_estudiante,
            "carrera": current.estudiante.carrera,
            "ciclo": current.estudiante.ciclo,
        }
    elif current.profesor:
        extra = {
            "codigo_profesor": current.profesor.codigo_profesor,
            "especialidad": current.profesor.especialidad,
        }

    return {
        "id_usuario": current.id_usuario,
        "nombres": current.nombres,
        "apellidos": current.apellidos,
        "correo": current.correo,
        "rol": current.rol,
        **extra,
    }
