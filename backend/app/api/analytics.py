"""Analítica de asistencia por rol (Fase 3)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_dependencies import CurrentUser
from app.models import Asistencia, Matricula, SesionAsistencia, Curso

router = APIRouter(prefix="/api/analytics", tags=["Analítica"])


@router.get("/my-summary")
def my_summary(current: CurrentUser, db: Session = Depends(get_db)):
    """Resumen de asistencia del estudiante autenticado."""
    if current.rol != "ESTUDIANTE":
        raise HTTPException(403, detail="Solo estudiantes.")
    est = current.estudiante
    if not est:
        raise HTTPException(404, detail="Perfil de estudiante no encontrado.")

    total = db.query(Asistencia).filter(Asistencia.id_estudiante == est.id_estudiante).count()
    presente = db.query(Asistencia).filter(
        Asistencia.id_estudiante == est.id_estudiante, Asistencia.estado == "PRESENTE"
    ).count()
    tardanza = db.query(Asistencia).filter(
        Asistencia.id_estudiante == est.id_estudiante, Asistencia.estado == "TARDANZA"
    ).count()
    ausente = db.query(Asistencia).filter(
        Asistencia.id_estudiante == est.id_estudiante, Asistencia.estado == "AUSENTE"
    ).count()

    porcentaje = round((presente + tardanza) / total * 100, 2) if total > 0 else 0.0

    return {
        "total_sesiones": total,
        "presente": presente,
        "tardanza": tardanza,
        "ausente": ausente,
        "porcentaje_asistencia": porcentaje,
    }


@router.get("/course/{id_curso}")
def course_summary(id_curso: int, current: CurrentUser, db: Session = Depends(get_db)):
    """Resumen de asistencia de un curso (profesor o admin)."""
    if current.rol not in ("PROFESOR", "ADMINISTRADOR"):
        raise HTTPException(403, detail="No autorizado.")

    # Sesiones de ese curso
    sesion_ids = [
        s.id_sesion for s in db.query(SesionAsistencia).filter(
            SesionAsistencia.id_curso == id_curso
        ).all()
    ]
    if not sesion_ids:
        return {"total_sesiones": 0, "alumnos": []}

    # Agrupar por estudiante
    from app.models import Estudiante
    matriculas = db.query(Matricula).filter(
        Matricula.id_curso == id_curso, Matricula.estado == True
    ).all()

    result = []
    for mat in matriculas:
        est = mat.estudiante
        asis = db.query(Asistencia).filter(
            Asistencia.id_sesion.in_(sesion_ids),
            Asistencia.id_estudiante == est.id_estudiante,
        ).all()
        presente = sum(1 for a in asis if a.estado == "PRESENTE")
        tardanza = sum(1 for a in asis if a.estado == "TARDANZA")
        ausente  = sum(1 for a in asis if a.estado == "AUSENTE")
        total    = len(asis)
        result.append({
            "nombre": f"{est.usuario.nombres} {est.usuario.apellidos}",
            "codigo": est.codigo_estudiante,
            "presente": presente,
            "tardanza": tardanza,
            "ausente": ausente,
            "total": total,
            "porcentaje": round((presente + tardanza) / total * 100, 2) if total else 0,
        })

    return {"total_sesiones": len(sesion_ids), "alumnos": result}


@router.get("/global")
def global_summary(current: CurrentUser, db: Session = Depends(get_db)):
    """Resumen global para el administrador."""
    if current.rol != "ADMINISTRADOR":
        raise HTTPException(403, detail="Solo administradores.")

    from app.models import Usuario, Estudiante, Profesor
    return {
        "total_usuarios": db.query(Usuario).filter(Usuario.estado == True).count(),
        "total_estudiantes": db.query(Estudiante).count(),
        "total_profesores": db.query(Profesor).count(),
        "total_cursos": db.query(Curso).filter(Curso.estado == True).count(),
        "total_asistencias": db.query(Asistencia).count(),
    }
