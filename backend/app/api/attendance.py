"""Registro y consulta de asistencias individuales (Fase 3)."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth_dependencies import CurrentUser
from app.models import Asistencia, SesionAsistencia, Matricula, Estudiante

router = APIRouter(prefix="/api/attendance", tags=["Asistencia"])


class MarkAttendanceRequest(BaseModel):
    id_sesion: int
    id_estudiante: int
    estado: str  # PRESENTE | TARDANZA | AUSENTE
    metodo_registro: str = "MANUAL"
    confianza_facial: float | None = None
    liveness: bool = False


@router.post("/mark", status_code=201)
def mark_attendance(
    payload: MarkAttendanceRequest,
    current: CurrentUser,
    db: Session = Depends(get_db),
):
    if current.rol not in ("PROFESOR", "ADMINISTRADOR"):
        raise HTTPException(403, detail="Solo el profesor o admin puede registrar asistencia.")
    if payload.estado not in ("PRESENTE", "TARDANZA", "AUSENTE"):
        raise HTTPException(422, detail="Estado inválido.")

    sesion = db.query(SesionAsistencia).filter(
        SesionAsistencia.id_sesion == payload.id_sesion
    ).first()
    if not sesion:
        raise HTTPException(404, detail="Sesión no encontrada.")

    # Verificar que el estudiante esté matriculado en ese curso
    matricula = db.query(Matricula).filter(
        Matricula.id_estudiante == payload.id_estudiante,
        Matricula.id_curso == sesion.id_curso,
        Matricula.estado == True,
    ).first()
    if not matricula:
        raise HTTPException(404, detail="El estudiante no está matriculado en este curso.")

    # Evitar duplicados
    exists = db.query(Asistencia).filter(
        Asistencia.id_sesion == payload.id_sesion,
        Asistencia.id_estudiante == payload.id_estudiante,
    ).first()
    if exists:
        raise HTTPException(409, detail="Ya existe asistencia registrada para este estudiante en esta sesión.")

    now = datetime.now(timezone.utc)
    asistencia = Asistencia(
        id_sesion=payload.id_sesion,
        id_estudiante=payload.id_estudiante,
        estado=payload.estado,
        hora_registro=now.time(),
        metodo_registro=payload.metodo_registro,
        confianza_facial=payload.confianza_facial,
        liveness=payload.liveness,
    )
    db.add(asistencia)
    db.commit()
    db.refresh(asistencia)
    return {"id_asistencia": asistencia.id_asistencia, "estado": asistencia.estado}


@router.get("/my")
def my_attendance(current: CurrentUser, db: Session = Depends(get_db)):
    """Estudiante consulta sus propias asistencias."""
    if current.rol != "ESTUDIANTE":
        raise HTTPException(403, detail="Solo los estudiantes pueden usar este endpoint.")
    est = current.estudiante
    if not est:
        raise HTTPException(404, detail="Perfil de estudiante no encontrado.")

    records = db.query(Asistencia).filter(
        Asistencia.id_estudiante == est.id_estudiante
    ).order_by(Asistencia.fecha_registro.desc()).all()

    return [
        {
            "id_asistencia": r.id_asistencia,
            "curso": r.sesion.curso.nombre if r.sesion and r.sesion.curso else None,
            "fecha": str(r.sesion.fecha) if r.sesion else None,
            "estado": r.estado,
            "metodo": r.metodo_registro,
        }
        for r in records
    ]


@router.get("/session/{id_sesion}")
def session_attendance(
    id_sesion: int,
    current: CurrentUser,
    db: Session = Depends(get_db),
):
    """Profesor o admin consultan asistencia de una sesión."""
    if current.rol not in ("PROFESOR", "ADMINISTRADOR"):
        raise HTTPException(403, detail="No autorizado.")

    records = db.query(Asistencia).filter(
        Asistencia.id_sesion == id_sesion
    ).all()
    return [
        {
            "id_asistencia": r.id_asistencia,
            "id_estudiante": r.id_estudiante,
            "nombre": f"{r.estudiante.usuario.nombres} {r.estudiante.usuario.apellidos}" if r.estudiante else None,
            "codigo": r.estudiante.codigo_estudiante if r.estudiante else None,
            "estado": r.estado,
            "hora_registro": str(r.hora_registro) if r.hora_registro else None,
            "metodo": r.metodo_registro,
        }
        for r in records
    ]
