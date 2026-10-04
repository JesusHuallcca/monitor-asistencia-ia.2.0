from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=200)


class RegisterRequest(BaseModel):
    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=200)
    rol: Literal["ESTUDIANTE", "PROFESOR"]

    codigo_estudiante: Optional[str] = Field(default=None, max_length=30)
    carrera: Optional[str] = Field(default=None, max_length=120)
    ciclo: Optional[str] = Field(default=None, max_length=20)

    codigo_profesor: Optional[str] = Field(default=None, max_length=30)
    especialidad: Optional[str] = Field(default=None, max_length=120)


class RefreshRequest(BaseModel):
    refresh_token: str
