"""SQLAlchemy ORM models – 12 tablas oficiales de monitor_asistencia_ia."""

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Date, Enum,
    ForeignKey, JSON, String, Text, Time, DECIMAL, func,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


# ─────────────────────────────────────────────────────────────────────────────
# 1. USUARIOS
# ─────────────────────────────────────────────────────────────────────────────
class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario    = Column(BigInteger, primary_key=True, autoincrement=True)
    nombres       = Column(String(100), nullable=False)
    apellidos     = Column(String(100), nullable=False)
    correo        = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    rol           = Column(Enum("ESTUDIANTE", "PROFESOR", "ADMINISTRADOR"), nullable=False)
    estado        = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())

    # Relaciones
    estudiante   = relationship("Estudiante", back_populates="usuario", uselist=False)
    profesor     = relationship("Profesor",   back_populates="usuario", uselist=False)
    chatbot_hist = relationship("ChatbotHistorial", back_populates="usuario")
    reportes     = relationship("ReporteGenerado",  back_populates="usuario")
    auditoria    = relationship("Auditoria",         back_populates="usuario")


# ─────────────────────────────────────────────────────────────────────────────
# 2. ESTUDIANTES
# ─────────────────────────────────────────────────────────────────────────────
class Estudiante(Base):
    __tablename__ = "estudiantes"

    id_estudiante     = Column(BigInteger, primary_key=True, autoincrement=True)
    id_usuario        = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), unique=True, nullable=False)
    codigo_estudiante = Column(String(30), nullable=False, unique=True)
    carrera           = Column(String(120))
    ciclo             = Column(String(20))

    usuario    = relationship("Usuario",    back_populates="estudiante")
    matriculas = relationship("Matricula",  back_populates="estudiante")
    asistencias = relationship("Asistencia", back_populates="estudiante")
    dato_facial = relationship("DatoFacial", back_populates="estudiante", uselist=False)


# ─────────────────────────────────────────────────────────────────────────────
# 3. PROFESORES
# ─────────────────────────────────────────────────────────────────────────────
class Profesor(Base):
    __tablename__ = "profesores"

    id_profesor     = Column(BigInteger, primary_key=True, autoincrement=True)
    id_usuario      = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), unique=True, nullable=False)
    codigo_profesor = Column(String(30), nullable=False, unique=True)
    especialidad    = Column(String(120))

    usuario = relationship("Usuario", back_populates="profesor")
    cursos  = relationship("Curso",   back_populates="profesor")


# ─────────────────────────────────────────────────────────────────────────────
# 4. CURSOS
# ─────────────────────────────────────────────────────────────────────────────
class Curso(Base):
    __tablename__ = "cursos"

    id_curso          = Column(BigInteger, primary_key=True, autoincrement=True)
    codigo            = Column(String(30), nullable=False, unique=True)
    nombre            = Column(String(150), nullable=False)
    seccion           = Column(String(30))
    periodo_academico = Column(String(20))
    modalidad         = Column(Enum("PRESENCIAL", "VIRTUAL", "HIBRIDO"), default="PRESENCIAL")
    aula              = Column(String(50))
    id_profesor       = Column(BigInteger, ForeignKey("profesores.id_profesor", ondelete="SET NULL"))
    estado            = Column(Boolean, default=True)

    profesor  = relationship("Profesor",  back_populates="cursos")
    horarios  = relationship("Horario",   back_populates="curso")
    matriculas = relationship("Matricula", back_populates="curso")
    sesiones  = relationship("SesionAsistencia", back_populates="curso")


# ─────────────────────────────────────────────────────────────────────────────
# 5. MATRÍCULAS
# ─────────────────────────────────────────────────────────────────────────────
class Matricula(Base):
    __tablename__ = "matriculas"

    id_matricula   = Column(BigInteger, primary_key=True, autoincrement=True)
    id_estudiante  = Column(BigInteger, ForeignKey("estudiantes.id_estudiante", ondelete="CASCADE"), nullable=False)
    id_curso       = Column(BigInteger, ForeignKey("cursos.id_curso",           ondelete="CASCADE"), nullable=False)
    fecha_matricula = Column(DateTime, server_default=func.now())
    estado         = Column(Boolean, default=True)

    estudiante = relationship("Estudiante", back_populates="matriculas")
    curso      = relationship("Curso",      back_populates="matriculas")


# ─────────────────────────────────────────────────────────────────────────────
# 6. HORARIOS
# ─────────────────────────────────────────────────────────────────────────────
class Horario(Base):
    __tablename__ = "horarios"

    id_horario   = Column(BigInteger, primary_key=True, autoincrement=True)
    id_curso     = Column(BigInteger, ForeignKey("cursos.id_curso", ondelete="CASCADE"), nullable=False)
    dia_semana   = Column(Enum("LUNES","MARTES","MIERCOLES","JUEVES","VIERNES","SABADO","DOMINGO"), nullable=False)
    hora_inicio  = Column(Time, nullable=False)
    hora_fin     = Column(Time, nullable=False)
    aula         = Column(String(50))

    curso = relationship("Curso", back_populates="horarios")


# ─────────────────────────────────────────────────────────────────────────────
# 7. SESIONES DE ASISTENCIA
# ─────────────────────────────────────────────────────────────────────────────
class SesionAsistencia(Base):
    __tablename__ = "sesiones_asistencia"

    id_sesion     = Column(BigInteger, primary_key=True, autoincrement=True)
    id_curso      = Column(BigInteger, ForeignKey("cursos.id_curso", ondelete="CASCADE"), nullable=False)
    fecha         = Column(Date, nullable=False)
    hora_inicio   = Column(Time, nullable=False)
    hora_fin      = Column(Time)
    estado        = Column(Enum("PROGRAMADA","ACTIVA","CERRADA"), default="PROGRAMADA")
    fecha_creacion = Column(DateTime, server_default=func.now())

    curso       = relationship("Curso",      back_populates="sesiones")
    asistencias = relationship("Asistencia", back_populates="sesion")


# ─────────────────────────────────────────────────────────────────────────────
# 8. ASISTENCIAS
# ─────────────────────────────────────────────────────────────────────────────
class Asistencia(Base):
    __tablename__ = "asistencias"

    id_asistencia    = Column(BigInteger, primary_key=True, autoincrement=True)
    id_sesion        = Column(BigInteger, ForeignKey("sesiones_asistencia.id_sesion", ondelete="CASCADE"), nullable=False)
    id_estudiante    = Column(BigInteger, ForeignKey("estudiantes.id_estudiante",     ondelete="CASCADE"), nullable=False)
    estado           = Column(Enum("PRESENTE","TARDANZA","AUSENTE"), nullable=False)
    hora_registro    = Column(Time)
    metodo_registro  = Column(Enum("FACIAL","MANUAL"), default="FACIAL")
    confianza_facial = Column(DECIMAL(5, 4))
    liveness         = Column(Boolean, default=False)
    fecha_registro   = Column(DateTime, server_default=func.now())

    sesion     = relationship("SesionAsistencia", back_populates="asistencias")
    estudiante = relationship("Estudiante",        back_populates="asistencias")


# ─────────────────────────────────────────────────────────────────────────────
# 9. DATOS FACIALES
# ─────────────────────────────────────────────────────────────────────────────
class DatoFacial(Base):
    __tablename__ = "datos_faciales"

    id_facial                = Column(BigInteger, primary_key=True, autoincrement=True)
    id_estudiante            = Column(BigInteger, ForeignKey("estudiantes.id_estudiante", ondelete="CASCADE"), unique=True, nullable=False)
    embedding                = Column(JSON)
    ruta_imagen_referencia   = Column(String(255))
    activo                   = Column(Boolean, default=True)
    fecha_registro           = Column(DateTime, server_default=func.now())

    estudiante = relationship("Estudiante", back_populates="dato_facial")


# ─────────────────────────────────────────────────────────────────────────────
# 10. CHATBOT HISTORIAL
# ─────────────────────────────────────────────────────────────────────────────
class ChatbotHistorial(Base):
    __tablename__ = "chatbot_historial"

    id_chat   = Column(BigInteger, primary_key=True, autoincrement=True)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    mensaje   = Column(Text, nullable=False)
    respuesta = Column(Text)
    intencion = Column(String(60))
    fecha     = Column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="chatbot_hist")


# ─────────────────────────────────────────────────────────────────────────────
# 11. REPORTES GENERADOS
# ─────────────────────────────────────────────────────────────────────────────
class ReporteGenerado(Base):
    __tablename__ = "reportes_generados"

    id_reporte    = Column(BigInteger, primary_key=True, autoincrement=True)
    id_usuario    = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    tipo          = Column(String(50), nullable=False)
    formato       = Column(Enum("XLSX","PDF"), nullable=False)
    filtros       = Column(JSON)
    ruta_archivo  = Column(String(255))
    fecha_creacion = Column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="reportes")


# ─────────────────────────────────────────────────────────────────────────────
# 12. AUDITORÍA
# ─────────────────────────────────────────────────────────────────────────────
class Auditoria(Base):
    __tablename__ = "auditoria"

    id_evento  = Column(BigInteger, primary_key=True, autoincrement=True)
    id_usuario = Column(BigInteger, ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), nullable=True)
    accion     = Column(String(120), nullable=False)
    entidad    = Column(String(80))
    entidad_id = Column(String(80))
    detalle    = Column(JSON)
    ip_origen  = Column(String(45))
    fecha      = Column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="auditoria")
