"""Admin panel – gestión global de usuarios y cursos (Fase 3)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_dependencies import get_current_user
from app.models import Usuario, Estudiante, Profesor, Curso, Asistencia

router = APIRouter(prefix="/api/admin", tags=["Administración"])


def _admin_only(current: Usuario = Depends(get_current_user)) -> Usuario:
    if current.rol != "ADMINISTRADOR":
        raise HTTPException(403, detail="Solo administradores.")
    return current


@router.get("/dashboard")
def admin_dashboard(
    current: Usuario = Depends(_admin_only),
    db: Session = Depends(get_db),
):
    total_u   = db.query(Usuario).filter(Usuario.estado == True).count()
    total_est = db.query(Estudiante).count()
    total_pro = db.query(Profesor).count()
    total_c   = db.query(Curso).filter(Curso.estado == True).count()
    total_a   = db.query(Asistencia).count()
    return {
        "usuarios_activos": total_u,
        "estudiantes": total_est,
        "profesores": total_pro,
        "cursos": total_c,
        "asistencias": total_a,
    }


@router.get("/users")
def list_all_users(
    current: Usuario = Depends(_admin_only),
    db: Session = Depends(get_db),
):
    users = db.query(Usuario).filter(Usuario.estado == True).order_by(Usuario.fecha_creacion.desc()).all()
    return [
        {"id_usuario": u.id_usuario, "nombres": u.nombres, "apellidos": u.apellidos,
         "correo": u.correo, "rol": u.rol}
        for u in users
    ]


@router.delete("/users/{id_usuario}")
def disable_user(
    id_usuario: int,
    current: Usuario = Depends(_admin_only),
    db: Session = Depends(get_db),
):
    user = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not user:
        raise HTTPException(404, detail="Usuario no encontrado.")
    user.estado = False
    db.commit()
    return {"message": f"Usuario {id_usuario} deshabilitado."}
