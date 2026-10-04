# Persona 3 (Jesus): Machine Learning / Estadística / Predicciones
"""
Servicio de estadística y analítica de asistencia.

Fórmulas (Manual Técnico §17):
  % asistencia = (Presentes + tardanzas) / sesiones × 100
  % ausencias  = Ausentes / sesiones × 100
  % tardanzas  = Tardanzas / sesiones × 100
  media, mediana, varianza, desv. estándar, tendencia semanal

Alcance por rol:
  estudiante → solo sus datos
  profesor   → alumnos de sus cursos
  administrador → global autorizado
"""
from __future__ import annotations

from datetime import date
from typing import Any, Sequence

from fastapi import HTTPException
from sqlalchemy.orm import Session

# Imports del proyecto principal (monitor_asistencia_ia)
from app.db.models import (
    AsignacionProfesor,
    Asistencia,
    Curso,
    Estudiante,
    Matricula,
    Profesor,
    SesionClase,
    Usuario,
)

# Paquete ai.ml (añadir raíz del repo al PYTHONPATH o instalar en editable)
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]  # monitor_asistencia_ia (repo root)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai.ml.features import (  # noqa: E402
    RegistroAsistencia,
    calcular_indicadores,
    desviacion_estandar,
    media,
    mediana,
    tendencia_semanal,
    varianza,
)

UMBRAL_ALERTA_PCT = 70.0


def _regs_from_rows(rows: Sequence[Any]) -> list[RegistroAsistencia]:
    out: list[RegistroAsistencia] = []
    for a in rows:
        curso_id = None
        if getattr(a, "sesion", None) is not None:
            curso_id = a.sesion.curso_id
        out.append(
            RegistroAsistencia(
                usuario_id=a.usuario_id,
                sesion_id=a.sesion_id,
                fecha=a.fecha if isinstance(a.fecha, date) else a.fecha,
                estado=a.estado,
                hora=getattr(a, "hora", None),
                curso_id=curso_id,
            )
        )
    return sorted(out, key=lambda r: (r.fecha, r.sesion_id))


def _estadistica_de_registros(
    regs: list[RegistroAsistencia],
    *,
    usuario_id: int,
    estudiante: Estudiante | None = None,
    usuario: Usuario | None = None,
    curso_id: int | None = None,
) -> dict[str, Any]:
    ind = calcular_indicadores(regs)
    # Serie binaria: 1 = asistió (PRESENTE|TARDANZA), 0 = ausente
    serie = [
        0.0 if r.estado.upper() == "AUSENTE" else 1.0
        for r in regs
    ]
    pct = ind.get("pct_asistencia")
    return {
        "usuario_id": usuario_id,
        "estudiante_id": estudiante.id if estudiante else None,
        "codigo": estudiante.codigo if estudiante else None,
        "nombres": usuario.nombres if usuario else None,
        "apellidos": usuario.apellidos if usuario else None,
        "curso_id": curso_id,
        "indicadores": ind,
        "media_asistencia_binaria": media(serie),
        "mediana_asistencia_binaria": mediana(serie),
        "varianza": varianza(serie),
        "desviacion_estandar": desviacion_estandar(serie),
        "tendencia_semanal": tendencia_semanal(regs),
        "alerta_baja_asistencia": (pct is not None and pct < UMBRAL_ALERTA_PCT),
        "umbral_alerta_pct": UMBRAL_ALERTA_PCT,
    }


def _cursos_del_profesor(db: Session, user: Usuario) -> list[int]:
    prof = db.query(Profesor).filter(Profesor.usuario_id == user.id).first()
    if not prof:
        return []
    rows = (
        db.query(AsignacionProfesor.curso_id)
        .filter(AsignacionProfesor.profesor_id == prof.id)
        .all()
    )
    return [r[0] for r in rows]


def estadistica_estudiante(
    db: Session,
    actor: Usuario,
    *,
    usuario_id: int | None = None,
    curso_id: int | None = None,
) -> dict[str, Any]:
    """Estadística de un estudiante (por defecto el propio actor si es estudiante)."""
    target_uid = usuario_id

    if actor.rol == "estudiante":
        target_uid = actor.id
        if usuario_id is not None and usuario_id != actor.id:
            raise HTTPException(status_code=403, detail="Solo puedes consultar tu propia estadística")
    elif actor.rol == "profesor":
        if target_uid is None:
            raise HTTPException(status_code=400, detail="Indica usuario_id del estudiante")
        cursos = _cursos_del_profesor(db, actor)
        if not cursos:
            raise HTTPException(status_code=403, detail="No tienes cursos asignados")
        # Verificar que el estudiante esté matriculado en al menos un curso del profesor
        est = db.query(Estudiante).filter(Estudiante.usuario_id == target_uid).first()
        if not est:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        ok = (
            db.query(Matricula)
            .filter(Matricula.estudiante_id == est.id, Matricula.curso_id.in_(cursos))
            .first()
        )
        if not ok:
            raise HTTPException(status_code=403, detail="El estudiante no pertenece a tus cursos")
    elif actor.rol == "administrador":
        if target_uid is None:
            raise HTTPException(status_code=400, detail="Indica usuario_id")
    else:
        raise HTTPException(status_code=403, detail="Rol no autorizado")

    q = db.query(Asistencia).filter(Asistencia.usuario_id == target_uid)
    if curso_id is not None:
        q = q.join(SesionClase, SesionClase.id == Asistencia.sesion_id).filter(
            SesionClase.curso_id == curso_id
        )
    rows = q.all()
    regs = _regs_from_rows(rows)
    est = db.query(Estudiante).filter(Estudiante.usuario_id == target_uid).first()
    usr = db.get(Usuario, target_uid)
    return _estadistica_de_registros(regs, usuario_id=target_uid, estudiante=est, usuario=usr, curso_id=curso_id)


def resumen_curso(db: Session, actor: Usuario, curso_id: int) -> dict[str, Any]:
    """Resumen estadístico de un curso (profesor del curso o administrador)."""
    curso = db.get(Curso, curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    if actor.rol == "profesor":
        if curso_id not in _cursos_del_profesor(db, actor):
            raise HTTPException(status_code=403, detail="No impartes este curso")
    elif actor.rol == "estudiante":
        raise HTTPException(status_code=403, detail="No autorizado a resumen de curso")
    elif actor.rol != "administrador":
        raise HTTPException(status_code=403, detail="Rol no autorizado")

    mats = db.query(Matricula).filter(Matricula.curso_id == curso_id).all()
    estudiantes_stats = []
    pcts = []
    all_regs: list[RegistroAsistencia] = []

    for m in mats:
        est = db.get(Estudiante, m.estudiante_id)
        if not est:
            continue
        rows = (
            db.query(Asistencia)
            .join(SesionClase, SesionClase.id == Asistencia.sesion_id)
            .filter(Asistencia.usuario_id == est.usuario_id, SesionClase.curso_id == curso_id)
            .all()
        )
        regs = _regs_from_rows(rows)
        all_regs.extend(regs)
        usr = db.get(Usuario, est.usuario_id)
        st = _estadistica_de_registros(
            regs, usuario_id=est.usuario_id, estudiante=est, usuario=usr, curso_id=curso_id
        )
        estudiantes_stats.append(st)
        if st["indicadores"].get("pct_asistencia") is not None:
            pcts.append(st["indicadores"]["pct_asistencia"])

    return {
        "curso_id": curso_id,
        "codigo": curso.codigo,
        "nombre": curso.nombre,
        "n_estudiantes": len(estudiantes_stats),
        "indicadores_grupo": calcular_indicadores(all_regs),
        "media_pct_asistencia": media(pcts),
        "mediana_pct_asistencia": mediana(pcts),
        "estudiantes": estudiantes_stats,
    }


def resumen_global(db: Session, actor: Usuario) -> dict[str, Any]:
    """Solo administrador."""
    if actor.rol != "administrador":
        raise HTTPException(status_code=403, detail="Solo el administrador puede ver el resumen global")

    rows = db.query(Asistencia).all()
    regs = _regs_from_rows(rows)
    cursos = db.query(Curso).filter(Curso.activo.is_(True)).all()
    por_curso = []
    for c in cursos:
        try:
            por_curso.append(resumen_curso(db, actor, c.id))
        except HTTPException:
            continue
    return {
        "total_registros": len(regs),
        "indicadores": calcular_indicadores(regs),
        "por_curso": por_curso,
    }
