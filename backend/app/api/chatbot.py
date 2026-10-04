"""Chatbot contextual y seguro por rol (Fase 4)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth_dependencies import CurrentUser
from app.models import (
    Asistencia, Matricula, SesionAsistencia, Curso,
    Estudiante, Profesor, ChatbotHistorial, Usuario
)

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


def _save_history(db: Session, id_usuario: int, mensaje: str, respuesta: str, intencion: str):
    db.add(ChatbotHistorial(
        id_usuario=id_usuario,
        mensaje=mensaje,
        respuesta=respuesta,
        intencion=intencion,
    ))
    db.commit()


# ─── Lógica ESTUDIANTE ────────────────────────────────────────────────────────
def _handle_student(msg: str, est: Estudiante, db: Session) -> tuple[str, str]:
    if any(w in msg for w in ["asistencia", "falta", "presente", "ausente", "tardanza"]):
        asis = db.query(Asistencia).filter(Asistencia.id_estudiante == est.id_estudiante).all()
        total = len(asis)
        presente = sum(1 for a in asis if a.estado == "PRESENTE")
        ausente  = sum(1 for a in asis if a.estado == "AUSENTE")
        tardanza = sum(1 for a in asis if a.estado == "TARDANZA")
        porc = round((presente + tardanza) / total * 100, 1) if total else 0
        return (
            f"📊 Tu asistencia: {presente} presente(s), {tardanza} tardanza(s), {ausente} ausencia(s) "
            f"de {total} sesión(es) registradas. Porcentaje: {porc}%.",
            "consulta_asistencia"
        )
    if any(w in msg for w in ["curso", "materia", "clase"]):
        mats = db.query(Matricula).filter(
            Matricula.id_estudiante == est.id_estudiante, Matricula.estado == True
        ).all()
        if not mats:
            return ("No tienes cursos matriculados actualmente.", "consulta_cursos")
        nombres = ", ".join(m.curso.nombre for m in mats)
        return (f"📚 Estás matriculado(a) en {len(mats)} curso(s): {nombres}.", "consulta_cursos")
    if any(w in msg for w in ["horario", "hora", "cuando"]):
        mats = db.query(Matricula).filter(
            Matricula.id_estudiante == est.id_estudiante, Matricula.estado == True
        ).all()
        result = []
        for m in mats:
            for h in m.curso.horarios:
                result.append(f"{m.curso.nombre}: {h.dia_semana} {h.hora_inicio}–{h.hora_fin}")
        if not result:
            return ("No hay horarios registrados para tus cursos.", "consulta_horarios")
        return ("🕒 Tus horarios:\n" + "\n".join(result), "consulta_horarios")
    return (
        "Hola 👋 Puedo ayudarte con: **asistencia**, **cursos** y **horarios**. ¿Qué quieres saber?",
        "saludo"
    )


# ─── Lógica PROFESOR ──────────────────────────────────────────────────────────
def _handle_professor(msg: str, prof: Profesor, db: Session) -> tuple[str, str]:
    if any(w in msg for w in ["alumno", "estudiante", "lista"]):
        curso_ids = [c.id_curso for c in prof.cursos]
        mats = db.query(Matricula).filter(Matricula.id_curso.in_(curso_ids), Matricula.estado == True).all()
        if not mats:
            return ("No tienes estudiantes matriculados en tus cursos.", "consulta_alumnos")
        nombres = ", ".join(
            f"{m.estudiante.usuario.nombres} {m.estudiante.usuario.apellidos}" for m in mats
        )
        return (f"👥 Tienes {len(mats)} estudiante(s): {nombres}.", "consulta_alumnos")
    if any(w in msg for w in ["curso", "materia", "asignatura"]):
        if not prof.cursos:
            return ("No tienes cursos asignados.", "consulta_cursos")
        cursos = ", ".join(c.nombre for c in prof.cursos)
        return (f"📚 Tus cursos: {cursos}.", "consulta_cursos")
    if any(w in msg for w in ["sesion", "sesión", "clase", "asistencia"]):
        curso_ids = [c.id_curso for c in prof.cursos]
        sesiones = db.query(SesionAsistencia).filter(
            SesionAsistencia.id_curso.in_(curso_ids)
        ).order_by(SesionAsistencia.fecha.desc()).limit(5).all()
        if not sesiones:
            return ("No hay sesiones registradas.", "consulta_sesiones")
        texto = "\n".join(f"{s.curso.nombre} – {s.fecha} ({s.estado})" for s in sesiones)
        return (f"📋 Últimas sesiones:\n{texto}", "consulta_sesiones")
    return (
        "Hola profesor 👋 Puedo ayudarte con: **alumnos**, **cursos** y **sesiones**.",
        "saludo"
    )


# ─── Lógica ADMINISTRADOR ─────────────────────────────────────────────────────
def _handle_admin(msg: str, db: Session) -> tuple[str, str]:
    if any(w in msg for w in ["usuario", "cuenta", "total"]):
        from app.models import Estudiante as Est, Profesor as Prof
        total_u = db.query(Usuario).filter(Usuario.estado == True).count()
        total_e = db.query(Est).count()
        total_p = db.query(Prof).count()
        return (
            f"📊 Sistema: {total_u} usuario(s) activo(s) — {total_e} estudiante(s), {total_p} profesor(es).",
            "consulta_global"
        )
    if any(w in msg for w in ["curso", "materia"]):
        total_c = db.query(Curso).filter(Curso.estado == True).count()
        return (f"📚 Total de cursos activos: {total_c}.", "consulta_cursos")
    if any(w in msg for w in ["asistencia"]):
        total_a = db.query(Asistencia).count()
        return (f"✅ Total de registros de asistencia: {total_a}.", "consulta_asistencia")
    return (
        "Hola Administrador 👋 Puedo mostrar estadísticas de **usuarios**, **cursos** y **asistencias**.",
        "saludo"
    )


# ─── Endpoint principal ───────────────────────────────────────────────────────
@router.post("/message", response_model=ChatResponse)
def chatbot_message(
    data: ChatRequest,
    current: CurrentUser,
    db: Session = Depends(get_db),
):
    msg = data.message.lower().strip()

    if current.rol == "ESTUDIANTE":
        est = current.estudiante
        if not est:
            return ChatResponse(response="Tu perfil de estudiante no está registrado aún.")
        response, intencion = _handle_student(msg, est, db)
    elif current.rol == "PROFESOR":
        prof = current.profesor
        if not prof:
            return ChatResponse(response="Tu perfil de profesor no está registrado aún.")
        response, intencion = _handle_professor(msg, prof, db)
    else:
        response, intencion = _handle_admin(msg, db)

    _save_history(db, current.id_usuario, data.message, response, intencion)
    return ChatResponse(response=response)
