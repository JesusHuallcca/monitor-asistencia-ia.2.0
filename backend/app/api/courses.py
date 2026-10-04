"""Cursos, sesiones de asistencia y matrículas (Fase 3)."""

from datetime import date, time as dtime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth_dependencies import CurrentUser
from app.models import Curso, Matricula, SesionAsistencia, Horario

router = APIRouter(prefix="/api/courses", tags=["Cursos"])


# ─── Endpoints de Cursos ──────────────────────────────────────────────────────
@router.get("/")
def list_courses(current: CurrentUser, db: Session = Depends(get_db)):
    if current.rol == "ADMINISTRADOR":
        cursos = db.query(Curso).filter(Curso.estado == True).all()
    elif current.rol == "PROFESOR":
        prof = current.profesor
        if not prof:
            return []
        cursos = prof.cursos
    else:  # ESTUDIANTE
        est = current.estudiante
        if not est:
            return []
        matriculas = db.query(Matricula).filter(
            Matricula.id_estudiante == est.id_estudiante,
            Matricula.estado == True
        ).all()
        cursos = [m.curso for m in matriculas]

    return [
        {
            "id_curso": c.id_curso, "codigo": c.codigo, "nombre": c.nombre,
            "seccion": c.seccion, "periodo_academico": c.periodo_academico,
            "modalidad": c.modalidad, "aula": c.aula,
        }
        for c in cursos
    ]


@router.get("/{id_curso}")
def get_course(id_curso: int, current: CurrentUser, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.id_curso == id_curso).first()
    if not curso:
        raise HTTPException(404, detail="Curso no encontrado.")
    return {
        "id_curso": curso.id_curso, "codigo": curso.codigo, "nombre": curso.nombre,
        "seccion": curso.seccion, "periodo_academico": curso.periodo_academico,
        "modalidad": curso.modalidad, "aula": curso.aula,
        "horarios": [
            {"dia": h.dia_semana, "inicio": str(h.hora_inicio), "fin": str(h.hora_fin)}
            for h in curso.horarios
        ]
    }


# ─── Endpoints de Sesiones ────────────────────────────────────────────────────
class CreateSesionRequest(BaseModel):
    id_curso: int
    fecha: date
    hora_inicio: dtime
    hora_fin: dtime | None = None


@router.post("/sessions", status_code=201)
def create_session(
    payload: CreateSesionRequest,
    current: CurrentUser,
    db: Session = Depends(get_db),
):
    if current.rol not in ("PROFESOR", "ADMINISTRADOR"):
        raise HTTPException(403, detail="Solo el profesor o admin puede crear sesiones.")

    sesion = SesionAsistencia(
        id_curso=payload.id_curso,
        fecha=payload.fecha,
        hora_inicio=payload.hora_inicio,
        hora_fin=payload.hora_fin,
        estado="PROGRAMADA",
    )
    db.add(sesion)
    db.commit()
    db.refresh(sesion)
    return {"id_sesion": sesion.id_sesion, "estado": sesion.estado}


@router.get("/sessions/{id_curso}")
def list_sessions(id_curso: int, current: CurrentUser, db: Session = Depends(get_db)):
    sesiones = db.query(SesionAsistencia).filter(
        SesionAsistencia.id_curso == id_curso
    ).order_by(SesionAsistencia.fecha.desc()).all()
    return [
        {
            "id_sesion": s.id_sesion, "fecha": str(s.fecha),
            "hora_inicio": str(s.hora_inicio), "estado": s.estado
        }
        for s in sesiones
    ]


@router.patch("/sessions/{id_sesion}/status")
def update_session_status(
    id_sesion: int,
    estado: str,
    current: CurrentUser,
    db: Session = Depends(get_db),
):
    if current.rol not in ("PROFESOR", "ADMINISTRADOR"):
        raise HTTPException(403, detail="No autorizado.")
    sesion = db.query(SesionAsistencia).filter(SesionAsistencia.id_sesion == id_sesion).first()
    if not sesion:
        raise HTTPException(404, detail="Sesión no encontrada.")
    if estado not in ("PROGRAMADA", "ACTIVA", "CERRADA"):
        raise HTTPException(422, detail="Estado inválido.")
    sesion.estado = estado
    db.commit()
    return {"id_sesion": id_sesion, "estado": sesion.estado}
