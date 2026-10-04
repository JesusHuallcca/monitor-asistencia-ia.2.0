"""
Modulo de Auditoria y Registro de Eventos
Registra acciones criticas en la tabla `auditoria` de MySQL.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import Auditoria
import logging

logger = logging.getLogger("auditoria")

def log_audit_event(
    db: Session,
    user_id: Optional[int],
    accion: str,
    entidad: Optional[str] = None,
    entidad_id: Optional[str] = None,
    detalle: Optional[Dict[str, Any]] = None,
    ip_origen: Optional[str] = None,
) -> None:
    """Registra una entrada de auditoria en la BD MySQL."""
    try:
        evento = Auditoria(
            id_usuario=user_id,
            accion=accion,
            entidad=entidad,
            entidad_id=str(entidad_id) if entidad_id is not None else None,
            detalle=detalle,
            ip_origen=ip_origen,
        )
        db.add(evento)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error al registrar evento de auditoria ({accion}): {e}")
