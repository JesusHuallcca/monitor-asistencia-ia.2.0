# Persona 3 (Jesus): Machine Learning / Estadística / Predicciones
"""
Endpoints de predicción (estimaciones de riesgo).

  GET  /api/predictions/me
  GET  /api/predictions/estudiante/{usuario_id}
  POST /api/predictions/train     (solo administrador)
  POST /api/predictions/evaluate  (solo administrador)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.db.database import get_db
from app.db.models import Usuario
from app.schemas.predictions import (
    EntrenarModeloOut,
    EvaluacionModeloOut,
    PrediccionRiesgoOut,
)
from app.services import prediction_service

router = APIRouter(prefix="/api/predictions", tags=["Persona 3 — Predicciones"])


@router.get("/me", response_model=PrediccionRiesgoOut)
def mi_prediccion(
    curso_id: int | None = Query(default=None),
    dia_proxima_sesion: int | None = Query(
        default=None, ge=0, le=6, description="0=lunes … 6=domingo"
    ),
    db: Session = Depends(get_db),
    actor: Usuario = Depends(get_current_user),
):
    return prediction_service.predecir_para_usuario(
        db, actor, curso_id=curso_id, dia_proxima_sesion=dia_proxima_sesion
    )


@router.get("/estudiante/{usuario_id}", response_model=PrediccionRiesgoOut)
def prediccion_estudiante(
    usuario_id: int,
    curso_id: int | None = Query(default=None),
    dia_proxima_sesion: int | None = Query(default=None, ge=0, le=6),
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("profesor", "administrador")),
):
    return prediction_service.predecir_para_usuario(
        db,
        actor,
        usuario_id=usuario_id,
        curso_id=curso_id,
        dia_proxima_sesion=dia_proxima_sesion,
    )


@router.post("/train", response_model=EntrenarModeloOut)
def entrenar(
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("administrador")),
):
    return prediction_service.entrenar_modelo(db, actor)


@router.post("/evaluate", response_model=EvaluacionModeloOut)
def evaluar(
    db: Session = Depends(get_db),
    actor: Usuario = Depends(require_roles("administrador")),
):
    return prediction_service.evaluar(db, actor)
