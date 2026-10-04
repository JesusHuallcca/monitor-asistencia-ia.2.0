# Persona 1 (Jhoshef): perfil del usuario autenticado
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PerfilOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    nombres: str
    apellidos: str
    rol: str
    estado: str
    tiene_login_facial: bool = False
    codigo: str | None = None
    carrera: str | None = None
    ciclo: int | None = None
    especialidad: str | None = None
    telefono: str | None = None


class PerfilActualizar(BaseModel):
    nombres: str | None = Field(default=None, min_length=1, max_length=100)
    apellidos: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, max_length=20)
    especialidad: str | None = Field(default=None, max_length=120)
    carrera: str | None = Field(default=None, max_length=120)
    ciclo: int | None = Field(default=None, ge=1, le=12)


class CambiarPassword(BaseModel):
    actual: str = Field(min_length=1, max_length=128)
    nueva: str = Field(min_length=8, max_length=128)