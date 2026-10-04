# Persona 4 (Jakelin): Chatbot — consultas MySQL parametrizadas (scope ya validado)
"""Manual §14: solo resultados autorizados; sin SQL libre generado por el modelo."""
from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

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


def _pct(presentes: int, tardanzas: int, ausentes: int) -> tuple[int, float | None, float | None, float | None]:
    total = presentes + tardanzas + ausentes
    if total == 0:
        return 0, None, None, None
    return (
        total,
        round((presentes + tardanzas) / total * 100, 1),
        round(ausentes / total * 100, 1),
        round(tardanzas / total * 100, 1),
    )


def ayuda(rol: str) -> str:
    if rol == "estudiante":
        return (
            "Puedo consultar solo tu información: cursos, porcentaje de asistencia, "
            "faltas y tardanzas. Ejemplos: «¿Cuántas faltas tengo?», «Muéstrame mis cursos»."
        )
    if rol == "profesor":
        return (
            "Puedo consultar tus cursos asignados y la asistencia de los alumnos matriculados en ellos. "
            "Ejemplos: «¿Qué cursos imparto?», «Resumen de asistencia de mis cursos»."
        )
    if rol == "administrador":
        return (
            "Puedo dar indicadores generales de usuarios, cursos y asistencia del sistema "
            "(sin contraseñas ni datos secretos)."
        )
    return "No hay ayuda disponible para tu rol."


def mis_cursos(db: Session, user: Usuario) -> str:
    est = db.query(Estudiante).filter(Estudiante.usuario_id == user.id).first()
    if not est:
        return "Tu cuenta no tiene perfil de estudiante asociado."
    rows = (
        db.query(Curso)
        .join(Matricula, Matricula.curso_id == Curso.id)
        .filter(Matricula.estudiante_id == est.id)
        .all()
    )
    if not rows:
        return "No tienes cursos matriculados actualmente."
    names = ", ".join(f"{c.codigo} — {c.nombre}" for c in rows)
    return f"Estás matriculado(a) en {len(rows)} curso(s): {names}."


def _conteo_asistencia_usuario(db: Session, usuario_id: int) -> Counter:
    estados = [
        r[0]
        for r in db.query(Asistencia.estado).filter(Asistencia.usuario_id == usuario_id).all()
    ]
    return Counter((e or "").upper() for e in estados)


def mi_asistencia(db: Session, user: Usuario) -> str:
    c = _conteo_asistencia_usuario(db, user.id)
    total, pct_a, pct_aus, pct_t = _pct(c["PRESENTE"], c["TARDANZA"], c["AUSENTE"])
    if total == 0:
        return "Aún no hay registros de asistencia para tu cuenta."
    return (
        f"Tu asistencia: {pct_a}% "
        f"(presentes: {c['PRESENTE']}, tardanzas: {c['TARDANZA']}, ausencias: {c['AUSENTE']}, "
        f"sobre {total} registro(s))."
    )


def mis_faltas(db: Session, user: Usuario) -> str:
    c = _conteo_asistencia_usuario(db, user.id)
    n = c["AUSENTE"]
    if c["PRESENTE"] + c["TARDANZA"] + n == 0:
        return "Aún no hay registros de asistencia; no se pueden contar faltas."
    return f"Tienes {n} ausencia(s) (estado AUSENTE) registradas."


def mis_tardanzas(db: Session, user: Usuario) -> str:
    c = _conteo_asistencia_usuario(db, user.id)
    n = c["TARDANZA"]
    if c["PRESENTE"] + n + c["AUSENTE"] == 0:
        return "Aún no hay registros de asistencia; no se pueden contar tardanzas."
    return f"Tienes {n} tardanza(s) registradas."


def _cursos_profesor(db: Session, user: Usuario) -> list[Curso]:
    prof = db.query(Profesor).filter(Profesor.usuario_id == user.id).first()
    if not prof:
        return []
    return (
        db.query(Curso)
        .join(AsignacionProfesor, AsignacionProfesor.curso_id == Curso.id)
        .filter(AsignacionProfesor.profesor_id == prof.id)
        .all()
    )


def cursos_profesor(db: Session, user: Usuario) -> str:
    cursos = _cursos_profesor(db, user)
    if not cursos:
        return "No tienes cursos asignados actualmente."
    names = ", ".join(f"{c.codigo} — {c.nombre}" for c in cursos)
    return f"Impartes {len(cursos)} curso(s): {names}."


def asistencia_curso_profesor(db: Session, user: Usuario) -> str:
    cursos = _cursos_profesor(db, user)
    if not cursos:
        return "No tienes cursos asignados para consultar asistencia."
    ids = [c.id for c in cursos]
    rows = (
        db.query(Asistencia.estado)
        .join(SesionClase, SesionClase.id == Asistencia.sesion_id)
        .filter(SesionClase.curso_id.in_(ids))
        .all()
    )
    c = Counter((r[0] or "").upper() for r in rows)
    total, pct_a, pct_aus, pct_t = _pct(c["PRESENTE"], c["TARDANZA"], c["AUSENTE"])
    if total == 0:
        return "Tus cursos aún no tienen registros de asistencia."
    return (
        f"Asistencia en tus {len(cursos)} curso(s): {pct_a}% asistencia, "
        f"{c['AUSENTE']} ausencias, {c['TARDANZA']} tardanzas "
        f"({total} registro(s) en total)."
    )


def resumen_usuarios(db: Session) -> str:
    rows = db.query(Usuario.rol, Usuario.estado).all()
    activos = [r for r in rows if (r[1] or "").lower() == "activo"]
    cont = Counter((r[0] or "").lower() for r in activos)
    return (
        f"Usuarios activos: {len(activos)}. "
        f"Estudiantes: {cont.get('estudiante', 0)}, "
        f"profesores: {cont.get('profesor', 0)}, "
        f"administradores: {cont.get('administrador', 0)}."
    )


def resumen_cursos(db: Session) -> str:
    n = db.query(Curso).filter(Curso.activo.is_(True)).count()
    return f"Hay {n} curso(s) activo(s) registrado(s) en el sistema."


def resumen_asistencia(db: Session) -> str:
    rows = db.query(Asistencia.estado).all()
    c = Counter((r[0] or "").upper() for r in rows)
    total, pct_a, pct_aus, pct_t = _pct(c["PRESENTE"], c["TARDANZA"], c["AUSENTE"])
    if total == 0:
        return "No hay registros de asistencia en el sistema."
    return (
        f"Asistencia global: {pct_a}% "
        f"(presentes {c['PRESENTE']}, tardanzas {c['TARDANZA']}, ausencias {c['AUSENTE']}, "
        f"total {total} registro(s))."
    )


def ejecutar(db: Session, user: Usuario, intencion: str) -> str:
    rol = (user.rol or "").lower()
    if intencion == "ayuda":
        return ayuda(rol)
    if intencion == "mis_cursos":
        return mis_cursos(db, user)
    if intencion == "mi_asistencia":
        return mi_asistencia(db, user)
    if intencion == "mis_faltas":
        return mis_faltas(db, user)
    if intencion == "mis_tardanzas":
        return mis_tardanzas(db, user)
    if intencion == "cursos_profesor":
        return cursos_profesor(db, user)
    if intencion == "asistencia_curso":
        return asistencia_curso_profesor(db, user)
    if intencion == "resumen_usuarios":
        return resumen_usuarios(db)
    if intencion == "resumen_cursos":
        return resumen_cursos(db)
    if intencion == "resumen_asistencia":
        return resumen_asistencia(db)
    return ayuda(rol)
