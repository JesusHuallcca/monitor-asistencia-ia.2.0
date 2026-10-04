"""Dependencias de autenticación para FastAPI.

Extrae el usuario actual del JWT y valida su rol.
"""

from __future__ import annotations
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models import Usuario

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Usuario:
    token = credentials.credentials
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = (
        db.query(Usuario)
        .filter(Usuario.id_usuario == int(user_id), Usuario.estado == True)
        .first()
    )
    if not user:
        raise credentials_exc
    return user


# Alias tipado para usar como parámetro de función de forma elegante
CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def require_roles(*roles: str):
    """Crea una dependencia que rechaza al usuario si no tiene alguno de los roles dados."""
    def _checker(current: Usuario = Depends(get_current_user)) -> Usuario:
        if current.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acción no permitida para el rol '{current.rol}'.",
            )
        return current
    return _checker
