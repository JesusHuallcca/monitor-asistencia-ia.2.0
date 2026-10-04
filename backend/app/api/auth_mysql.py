from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt, os
from app.core.database import get_db, Base
from app.models import User
from pydantic import BaseModel, EmailStr, validator

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

# Pydantic schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None
    role: str
    @validator('role')
    def role_allowed(cls, v):
        if v not in ('admin', 'teacher', 'student'):
            raise ValueError('Rol no permitido')
        return v

# Helper functions

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# JWT helpers (same as in auth.py)
def create_access_token(data: dict):
    return jwt.encode(data, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    hashed = get_password_hash(payload.password)
    user = User(
        username=payload.username,
        password_hash=hashed,
        role=payload.role,
        full_name=payload.full_name,
        email=payload.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Cuenta creada", "user_id": user.id}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    access_token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}
