# Persona 3 (Jesus): schemas de predicciones (estimaciones)
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PrediccionRiesgoOut(BaseModel):
    usuario_id: int
    probabilidad_riesgo: float = Field(ge=0, le=1)
    riesgo_estimado: bool
    nivel: str  # bajo | medio | alto
    umbral: float
    indicadores_recientes: dict[str, Any]
    es_estimacion: bool = True
    mensaje: str
    algorithm: str | None = None
    modelo_disponible: bool = True


class EntrenarModeloOut(BaseModel):
    ok: bool
    n_samples: int | None = None
    n_train: int | None = None
    n_test: int | None = None
    metrics_test: dict[str, float | None] | None = None
    model_path: str | None = None
    note: str | None = None
    error: str | None = None


class EvaluacionModeloOut(BaseModel):
    n_samples: int
    metrics: dict[str, float | None] | None = None
    confusion_matrix: list[list[int]] | None = None
    note: str | None = None
    error: str | None = None
