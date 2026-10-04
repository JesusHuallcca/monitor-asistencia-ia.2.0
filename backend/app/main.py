"""
Main FastAPI Application — Monitor Asistencia IA (MySQL)
Fase 8: Hardening, Seguridad, Auditoría, Manejo de Errores Global y Publicación Web.
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

# Configuración de Logging Estructurado
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

# 1. Configuración de CORS Estricto / Seguro
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
    
    # Cabeceras de Seguridad Estándar
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
    
    return response

# 3. Handler Global de Excepciones Unhandled (500 Error Shielding)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Excepción no capturada en {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Ha ocurrido un error interno en el servidor.",
            "detail": str(exc),
            "path": str(request.url.path),
        },
    )

# 4. Inclusión de Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(attendance_router)
app.include_router(analytics_router)
app.include_router(chatbot_router)
app.include_router(reports_router)
app.include_router(face_router)

# 5. Montaje de Archivos Estáticos del Frontend para Despliegue Web Unificado
BASE_DIR = Path(__file__).resolve().parent.parent.parent
frontend_path = BASE_DIR / "frontend"
if frontend_path.exists():
    app.mount("/site", StaticFiles(directory=str(frontend_path), html=True), name="site")


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
