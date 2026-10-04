# Integración Login + Dashboard Administrador

## Qué se añadió (versión MySQL)

- Login académico para **ESTUDIANTE / PROFESOR** usando MySQL.
- Login separado para **ADMINISTRADOR** usando la tabla `users` en MySQL.
- Backend con **FastAPI** y **SQLAlchemy** conectado a MySQL.
- Validación de credenciales con **bcrypt**.
- Generación de **JWT** propio (sin Supabase).
- Redirección automática según rol.
- Protección de dashboards por rol.
- Dashboard de administrador conectado a MySQL.

## 1. Variables de entorno

Crea un archivo `.env` en la raíz del backend con los siguientes datos (ajusta los valores a tu entorno MySQL):

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=attendance_db
DB_USER=root
DB_PASSWORD=tu_contraseña
JWT_SECRET=una_clave_secreta_para_jwt
JWT_ALGORITHM=HS256
```

## 2. Instalar dependencias del backend

Desde la carpeta `backend/` (crea un entorno virtual si lo deseas) ejecuta:

```powershell
python -m pip install fastapi uvicorn sqlalchemy pymysql python-dotenv bcrypt python-jose
```

## 3. Modelo de datos (SQLAlchemy)

```python
from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('admin','teacher','student'), nullable=False)
    full_name = Column(String(100))
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

## 4. Crear el primer administrador

```python
import bcrypt, os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Base

DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_admin():
    pwd = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    admin = User(username="admin", password_hash=pwd, role="admin", full_name="Administrador de Prueba", email="admin@example.com")
    db = SessionLocal()
    db.add(admin)
    db.commit()
    db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    create_admin()
```
Ejecuta el script con `python create_admin.py`.

## 5. Endpoints de autenticación (FastAPI)

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt, os

app = FastAPI()

# Carga de variables de entorno
from dotenv import load_dotenv
load_dotenv()

# Dependencia de DB

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return None
    return user

def create_access_token(data: dict):
    return jwt.encode(data, os.getenv("JWT_SECRET"), algorithm=os.getenv("JWT_ALGORITHM"))

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    access_token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}
```

## 6. Protección de rutas con JWT

```python
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=[os.getenv("JWT_ALGORITHM")])
        username: str = payload.get("sub")
        role: str = payload.get("role")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return {"user": user, "role": role}
```

## 7. Dashboard protegido

```python
@app.get("/admin/dashboard")
async def admin_dashboard(current: dict = Depends(get_current_user)):
    if current["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    # Aquí puedes consultar datos de MySQL y devolverlos como JSON
    return {"msg": "Datos del dashboard para admin"}
```

## 8. Frontend (login simple)

```html
<!-- login.html -->
<form id="loginForm">
  <input type="text" name="username" placeholder="Usuario" required />
  <input type="password" name="password" placeholder="Contraseña" required />
  <button type="submit">Entrar</button>
</form>
<script>
  document.getElementById('loginForm').addEventListener('submit', async e => {
    e.preventDefault();
    const data = new URLSearchParams(new FormData(e.target));
    const resp = await fetch('http://127.0.0.1:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: data
    });
    const json = await resp.json();
    if (resp.ok) {
      localStorage.setItem('token', json.access_token);
      localStorage.setItem('role', json.role);
      if (json.role === 'admin') location.href = '/dashboard/index.html';
      // agregar rutas para teacher/student
    } else {
      alert('Login falló: ' + json.detail);
    }
  });
</script>
```

## 9. Ejecutar la aplicación

```powershell
uvicorn main:app --reload
```

Ahora el dashboard y el login usan únicamente MySQL como fuente de datos y autenticación.

## Qué se agregó

- Login académico para **ESTUDIANTE / PROFESOR**.
- Login separado para **ADMINISTRADOR**.
- Integración de login con **FastAPI + Supabase Auth**.
- Validación del JWT en el backend.
- Redirección automática según rol.
- Protección de dashboards por rol.
- Dashboard de administrador conectado a Supabase.
- Chatbot global en el dashboard de administrador.
- Pantalla de acceso facial con cámara funcional como interfaz; la comparación biométrica real queda para la etapa de reconocimiento facial.

## 1. Variables de entorno

Copia:

```text
backend/.env.example
```

como:

```text
backend/.env
```

y completa:

```env
SUPABASE_URL=...
SUPABASE_PUBLISHABLE_KEY=...
SUPABASE_SECRET_KEY=...
```

La `SUPABASE_SECRET_KEY` nunca debe ir al frontend.

## 2. Instalar dependencias

Desde `backend/` con el entorno virtual activo:

```powershell
python -m pip install -r requirements.txt
```

## 3. Configurar perfil automático en Supabase

Ejecuta una vez en **Supabase > SQL Editor**:

```text
database/supabase_auth_setup.sql
```

## 4. Crear el primer administrador

Desde `backend/`:

```powershell
python scripts/create_admin.py
```

El script crea el usuario en Supabase Auth y su fila en `public.perfiles` con rol `ADMINISTRADOR`.

## 5. Levantar FastAPI

```powershell
python -m uvicorn app.main:app --reload
```

Pruebas:

- `http://127.0.0.1:8000/docs`
- `GET /api/test-supabase`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/admin/dashboard`

## 6. Levantar frontend

Usa Live Server en VS Code y abre:

```text
frontend/login/portal_login.html
```

Para administrador:

```text
frontend/login/admin_login.html
```

## Rutas por rol

- ESTUDIANTE -> `frontend/estudiante/dashboard.html`
- PROFESOR -> `frontend/profesor/dashboard.html`
- ADMINISTRADOR -> `frontend/administrador/dashboard.html`

## Seguridad implementada

El frontend guarda temporalmente el access token para el prototipo y lo envía como:

```text
Authorization: Bearer <token>
```

FastAPI valida el token contra Supabase Auth y luego obtiene el rol desde `public.perfiles`.
El backend impide que un usuario con rol incorrecto consulte `/api/admin/dashboard`.

## Archivos nuevos principales

```text
backend/app/core/supabase_client.py
backend/app/core/auth_dependencies.py
backend/app/api/auth.py
backend/app/api/admin.py
backend/scripts/create_admin.py
backend/.env.example

database/supabase_auth_setup.sql

frontend/login/portal_login.html
frontend/login/admin_login.html
frontend/login/face_login.html
frontend/administrador/dashboard.html
frontend/assets/css/login.css
frontend/assets/css/admin.css
frontend/assets/js/api.js
frontend/assets/js/auth.js
frontend/assets/js/login.js
frontend/assets/js/admin.js
```

## Pendiente para la siguiente etapa

- Registro controlado de estudiantes/profesores.
- Recuperación de contraseña.
- Reconocimiento facial real y liveness.
- CRUD completo de usuarios/cursos desde administrador.
- Reportes Excel/PDF.
- RLS completo para consultas directas con JWT de usuario.

## Registro académico integrado

El Portal Académico ahora incluye un botón **Registrarse** que abre `frontend/login/registro.html`.
El formulario permite crear únicamente cuentas `ESTUDIANTE` o `PROFESOR`; los administradores se siguen creando desde backend con `scripts/create_admin.py`.

Endpoint nuevo:

- `POST /api/auth/register`

Al registrarse, el backend crea:

- usuario en Supabase Auth;
- registro en `public.perfiles`;
- registro en `public.estudiantes` o `public.profesores`, según el rol.

Después del registro, el frontend inicia sesión y redirige automáticamente al dashboard correspondiente.

## CSS separados por pantalla de acceso
- `frontend/assets/css/portal-login.css`: Portal Académico (estudiante/profesor).
- `frontend/assets/css/registro.css`: Registro académico.
- `frontend/assets/css/admin-login.css`: Login exclusivo del administrador.
- `frontend/assets/css/face-login.css`: Acceso facial.

El antiguo `login.css` compartido fue retirado para evitar que estilos de una pantalla afecten a otra.


## Política final de creación de cuentas
- No existe registro público desde Portal Académico.
- ADMINISTRADOR: puede crear PROFESOR y ESTUDIANTE.
- PROFESOR: puede crear únicamente ESTUDIANTE.
- ESTUDIANTE: no puede crear cuentas.
- Endpoint protegido: POST /api/users/create con Bearer token.
- Pantallas: administrador/crear_profesor.html, administrador/crear_estudiante.html y profesor/crear_estudiante.html.
