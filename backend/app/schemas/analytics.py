# Persona 3 (Jesus): schemas de estadística y analítica
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IndicadoresOut(BaseModel):
    sesiones: int
    presentes: int
    tardanzas: int
    ausentes: int
    pct_asistencia: float | None = None
    pct_ausencias: float | None = None
    pct_tardanzas: float | None = None


class TendenciaSemanaOut(BaseModel):
    anio: int
    semana: int
    sesiones: int
    pct_asistencia: float | None = None
    ausentes: int


class EstadisticaEstudianteOut(BaseModel):
    usuario_id: int
    estudiante_id: int | None = None
    codigo: str | None = None
    nombres: str | None = None
    apellidos: str | None = None
    curso_id: int | None = None
    indicadores: IndicadoresOut
    media_asistencia_binaria: float | None = Field(
        default=None,
        description="Media de 1=asistió (PRESENTE|TARDANZA), 0=ausente",
    )
    mediana_asistencia_binaria: float | None = None
    varianza: float | None = None
    desviacion_estandar: float | None = None
    tendencia_semanal: list[TendenciaSemanaOut] = []
    alerta_baja_asistencia: bool = False
    umbral_alerta_pct: float = 70.0


class ResumenCursoOut(BaseModel):
    curso_id: int
    codigo: str | None = None
    nombre: str | None = None
    n_estudiantes: int
    indicadores_grupo: IndicadoresOut
    media_pct_asistencia: float | None = None
    mediana_pct_asistencia: float | None = None
    estudiantes: list[EstadisticaEstudianteOut] = []


class ResumenGlobalOut(BaseModel):
    total_registros: int
    indicadores: IndicadoresOut
    por_curso: list[ResumenCursoOut] = []
