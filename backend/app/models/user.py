"""SQLAlchemy User model for MySQL backend.

This model is used by the authentication routes and the test‑data scripts.
It lives in ``app.models.user`` so that imports like ``from app.models.user import User`` work.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # e.g. "admin", "teacher", "dmi"
    full_name = Column(String(100), nullable=True)
    email = Column(String(120), nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role}>"
