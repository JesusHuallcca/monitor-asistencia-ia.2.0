# Persona 3 (Jesus): Machine Learning / Estadística / Predicciones
"""
Servicio de predicción de riesgo de ausencia/tardanza.

La salida es siempre una ESTIMACIÓN (es_estimacion=True).
No se inventan métricas del modelo: se leen del entrenamiento real o se indica
que el modelo no está disponible.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import (
    AsignacionProfesor,
    Asistencia,
    Estudiante,
    Matricula,
    Profesor,
    SesionClase,
    Usuario,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]  # monitor_asistencia_ia (repo root)
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

def _ml():
    """Import diferido: no tumba uvicorn si sklearn falla."""
    from ai.ml.features import RegistroAsistencia
    from ai.ml.predict import predecir_riesgo
    from ai.ml.train import DEFAULT_MODEL_PATH, entrenar
    from ai.ml.evaluate import evaluar_modelo
    return RegistroAsistencia, predecir_riesgo, DEFAULT_MODEL_PATH, entrenar, evaluar_modelo
from ai.ml.features import RegistroAsistencia

def _historial_usuario(db: Session, usuario_id: int, curso_id: int | None = None) -> list[RegistroAsistencia]:
    
    q = db.query(Asistencia).filter(Asistencia.usuario_id == usuario_id)
    if curso_id is not None:
        q = q.join(SesionClase, SesionClase.id == Asistencia.sesion_id).filter(
            SesionClase.curso_id == curso_id
        )
    rows = q.order_by(Asistencia.fecha.asc(), Asistencia.sesion_id.asc()).all()
    out: list[RegistroAsistencia] = []
    for a in rows:
        curso = None
        if a.sesion is not None:
            curso = a.sesion.curso_id
        out.append(
            RegistroAsistencia(
                usuario_id=a.usuario_id,
                sesion_id=a.sesion_id,
                fecha=a.fecha,
                estado=a.estado,
                hora=a.hora,
                curso_id=curso,
            )
        )
    return out


def _assert_puede_ver(db: Session, actor: Usuario, target_uid: int) -> None:
    if actor.rol == "estudiante":
        if actor.id != target_uid:
            raise HTTPException(status_code=403, detail="Solo puedes ver tu propia predicción")
        return
    if actor.rol == "profesor":
        prof = db.query(Profesor).filter(Profesor.usuario_id == actor.id).first()
        if not prof:
            raise HTTPException(status_code=403, detail="Perfil de profesor no encontrado")
        cursos = [
            r[0]
            for r in db.query(AsignacionProfesor.curso_id)
            .filter(AsignacionProfesor.profesor_id == prof.id)
            .all()
        ]
        est = db.query(Estudiante).filter(Estudiante.usuario_id == target_uid).first()
        if not est:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        ok = (
            db.query(Matricula)
            .filter(Matricula.estudiante_id == est.id, Matricula.curso_id.in_(cursos or [-1]))
            .first()
        )
        if not ok:
            raise HTTPException(status_code=403, detail="El estudiante no está en tus cursos")
        return
    if actor.rol == "administrador":
        return
    raise HTTPException(status_code=403, detail="Rol no autorizado")

_, predecir_riesgo, DEFAULT_MODEL_PATH, entrenar, evaluar_modelo = _ml()
def predecir_para_usuario(
    db: Session,
    actor: Usuario,
    *,
    usuario_id: int | None = None,
    curso_id: int | None = None,
    dia_proxima_sesion: int | None = None,
) -> dict[str, Any]:
    target = usuario_id if usuario_id is not None else actor.id
    if actor.rol == "estudiante":
        target = actor.id
    _assert_puede_ver(db, actor, target)

    hist = _historial_usuario(db, target, curso_id)
    if len(hist) < 1:
        return {
            "usuario_id": target,
            "probabilidad_riesgo": 0.0,
            "riesgo_estimado": False,
            "nivel": "bajo",
            "umbral": 0.5,
            "indicadores_recientes": {
                "sesiones": 0,
                "presentes": 0,
                "tardanzas": 0,
                "ausentes": 0,
                "pct_asistencia": None,
                "pct_ausencias": None,
                "pct_tardanzas": None,
            },
            "es_estimacion": True,
            "mensaje": "Sin historial suficiente para estimar. Se requiere al menos un registro de asistencia.",
            "algorithm": None,
            "modelo_disponible": DEFAULT_MODEL_PATH.exists(),
        }

    if dia_proxima_sesion is None:
        dia_proxima_sesion = date.today().weekday()

    try:
        result = predecir_riesgo(
            hist,
            dia_proxima_sesion=dia_proxima_sesion,
            model_path=DEFAULT_MODEL_PATH,
        )
    except FileNotFoundError:
        return {
            "usuario_id": target,
            "probabilidad_riesgo": 0.0,
            "riesgo_estimado": False,
            "nivel": "bajo",
            "umbral": 0.5,
            "indicadores_recientes": {},
            "es_estimacion": True,
            "mensaje": (
                "Modelo no entrenado aún. Un administrador debe ejecutar "
                "POST /api/predictions/train cuando haya datos suficientes."
            ),
            "algorithm": None,
            "modelo_disponible": False,
        }

    result["usuario_id"] = target
    result["modelo_disponible"] = True
    # No devolver features crudas al cliente por defecto (menos ruido en UI)
    result.pop("features_usadas", None)
    return result


def _historial_completo(db: Session) -> dict[int, list[RegistroAsistencia]]:
    rows = db.query(Asistencia).order_by(Asistencia.usuario_id, Asistencia.fecha).all()
    por: dict[int, list[RegistroAsistencia]] = {}
    for a in rows:
        por.setdefault(a.usuario_id, []).append(
            RegistroAsistencia(
                usuario_id=a.usuario_id,
                sesion_id=a.sesion_id,
                fecha=a.fecha,
                estado=a.estado,
                hora=a.hora,
                curso_id=a.sesion.curso_id if a.sesion else None,
            )
        )
    return por


def entrenar_modelo(db: Session, actor: Usuario) -> dict[str, Any]:
    """Solo administrador. Entrena con el historial real de la BD."""
    if actor.rol != "administrador":
        raise HTTPException(status_code=403, detail="Solo el administrador puede entrenar el modelo")

    data = _historial_completo(db)
    try:
        res = entrenar(data)
        return {
            "ok": True,
            "n_samples": res.n_samples,
            "n_train": res.n_train,
            "n_test": res.n_test,
            "metrics_test": res.metrics_test,
            "model_path": res.model_path,
            "note": res.note,
            "error": None,
        }
    except ValueError as e:
        return {
            "ok": False,
            "n_samples": None,
            "n_train": None,
            "n_test": None,
            "metrics_test": None,
            "model_path": None,
            "note": None,
            "error": str(e),
        }


def evaluar(db: Session, actor: Usuario) -> dict[str, Any]:
    if actor.rol != "administrador":
        raise HTTPException(status_code=403, detail="Solo el administrador puede evaluar el modelo")
    data = _historial_completo(db)
    try:
        return evaluar_modelo(data)
    except FileNotFoundError as e:
        return {"n_samples": 0, "metrics": None, "error": str(e)}
