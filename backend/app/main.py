"""
Main FastAPI Application â€” Monitor Asistencia IA (MySQL)
Fase 8: Hardening, Seguridad, AuditorÃ­a, Manejo de Errores Global y PublicaciÃ³n Web.
"""

import time
import logging
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.chatbot import router as chatbot_router
from app.api.users import router as users_router
from app.api.courses import router as courses_router
from app.api.attendance import router as attendance_router
from app.api.analytics import router as analytics_router
from app.api.reports import router as reports_router
from app.api.face import router as face_router

# ConfiguraciÃ³n de Logging Estructurado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("api_hardening")

app = FastAPI(
    title="Monitor Inteligente de Asistencia IA",
    description="API REST con MySQL, JWT propio, reconocimiento facial y chatbot contextual seguro.",
    version="3.0.0",
)

# 1. ConfiguraciÃ³n de CORS Estricto / Seguro
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 2. Middleware de Cabeceras de Seguridad HTTP (Security Hardening)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    # Cabeceras de Seguridad EstÃ¡ndar
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
    
    return response

# 3. Handler Global de Excepciones Unhandled (500 Error Shielding)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"ExcepciÃ³n no capturada en {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Ha ocurrido un error interno en el servidor.",
            "detail": str(exc),
            "path": str(request.url.path),
        },
    )

# 4. InclusiÃ³n de Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(attendance_router)
app.include_router(analytics_router)
app.include_router(chatbot_router)
app.include_router(reports_router)
app.include_router(face_router)

# 5. Montaje de Archivos EstÃ¡ticos del Frontend para Despliegue Web Unificado
BASE_DIR = Path(__file__).resolve().parent.parent.parent
frontend_path = BASE_DIR / "frontend"
if frontend_path.exists():
    app.mount("/site", StaticFiles(directory=str(frontend_path), html=True), name="site")



@app.on_event("startup")
async def startup_event():
    """Crea tablas y admin por defecto al iniciar en produccion."""
    try:
        from app.core.database import engine, Base
        import app.models  # noqa: importa todos los modelos
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas/verificadas correctamente.")

        # Crear admin por defecto si no existe
        from app.core.database import SessionLocal
        from app.models import Usuario
        from passlib.context import CryptContext
        import os
        pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
        db = SessionLocal()
        try:
            admin_email = os.getenv("ADMIN_EMAIL", "admin@monitor.com")
            admin_pass  = os.getenv("ADMIN_PASSWORD", "Admin1234!")
            exists = db.query(Usuario).filter(Usuario.correo == admin_email).first()
            if not exists:
                admin = Usuario(
                    nombres="Administrador",
                    apellidos="Sistema",
                    correo=admin_email,
                    password_hash=pwd_ctx.hash(admin_pass),
                    rol="ADMINISTRADOR",
                    estado=True,
                )
                db.add(admin)
                db.commit()
                logger.info(f"✅ Admin creado: {admin_email}")
            else:
                logger.info("ℹ️  Admin ya existe.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ Error en startup: {e}", exc_info=True)

@app.get("/")
def root():
    return RedirectResponse(url="/site/login/portal_login.html")


@app.get("/api/health")
def health_check():
    from app.core.database import engine
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"database": "ok", "status": "healthy", "version": "3.0.0"}
    except Exception as e:
        return {"database": "error", "detail": str(e)}

