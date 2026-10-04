# Persona 4 (Jakelin): Chatbot — política de alcance por rol
# Manual §14: el LLM/no-reglas no accede a MySQL libre; FastAPI decide intención y scope.
"""
Intenciones reconocidas (reglas, sin SQL libre del modelo):
  mis_cursos | mi_asistencia | mis_faltas | mis_tardanzas
  cursos_profesor | asistencia_curso
  resumen_usuarios | resumen_cursos | resumen_asistencia
  denegado | ayuda
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IntentResult:
    intencion: str
    denegado: bool = False
    motivo: str | None = None


def clasificar_intencion(mensaje: str, rol: str) -> IntentResult:
    text = (mensaje or "").lower().strip()
    rol = (rol or "").lower()

    # Intentos de salir del scope — denegar siempre
    prohibido_estudiante = any(
        w in text
        for w in (
            "otro estudiante",
            "otro alumno",
            "contraseña",
            "password",
            "administrador",
            "todos los alumnos",
            "lista completa de usuarios",
        )
    )
    if rol == "estudiante" and prohibido_estudiante:
        return IntentResult("denegado", True, "No puedes consultar datos de otros usuarios ni información administrativa.")

    if rol == "profesor" and any(
        w in text for w in ("administrador", "contraseña", "password", "todos los cursos del sistema")
    ):
        return IntentResult("denegado", True, "No tienes acceso a información administrativa ni global del sistema.")

    if any(w in text for w in ("contraseña", "password", "hash", "token secreto", "secret_key")):
        return IntentResult("denegado", True, "Esa información no está disponible.")

    # Clasificación por palabras clave
    if any(w in text for w in ("ayuda", "qué puedes", "que puedes", "hola", "buenos días", "buenas")):
        return IntentResult("ayuda")

    if rol == "estudiante":
        if any(w in text for w in ("curso", "matricul")):
            return IntentResult("mis_cursos")
        if any(w in text for w in ("falta", "ausencia", "ausente")):
            return IntentResult("mis_faltas")
        if any(w in text for w in ("tardanza", "tarde", "puntual")):
            return IntentResult("mis_tardanzas")
        if any(w in text for w in ("asistencia", "porcentaje", "%", "estadística", "estadistica")):
            return IntentResult("mi_asistencia")
        return IntentResult("ayuda")

    if rol == "profesor":
        if any(w in text for w in ("curso", "imparto", "asignado")):
            return IntentResult("cursos_profesor")
        if any(w in text for w in ("asistencia", "falt", "ausenc", "tardanza", "alumno", "estudiante")):
            return IntentResult("asistencia_curso")
        return IntentResult("ayuda")

    if rol == "administrador":
        if any(w in text for w in ("usuario", "estudiante", "profesor", "cuenta")):
            return IntentResult("resumen_usuarios")
        if "curso" in text:
            return IntentResult("resumen_cursos")
        if any(w in text for w in ("asistencia", "ausenc", "falt", "tardanza", "global", "general")):
            return IntentResult("resumen_asistencia")
        return IntentResult("ayuda")

    return IntentResult("denegado", True, "Rol no autorizado para el chatbot.")
