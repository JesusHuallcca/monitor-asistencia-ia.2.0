# Monitor Inteligente de Asistencia con IA (SENATI)

Base unificada a partir de `monitor-asistencia-ia-main`, con integración de:

- **Persona 1 (Jhoshef):** Login / Usuarios / Seguridad + Login Facial + Auditoría
- **Persona 2 (Rouss):** Asistencia en vivo / Cámara / IA facial
- **Persona 3 (Jesus):** Machine Learning / Estadística / Predicciones (**integrado**)

## Roles definitivos (solo 3)

| Rol | Portal de login | Puede |
|-----|-----------------|--------|
| `estudiante` | Académico (`/api/auth/login`) | Ver su asistencia y datos propios |
| `profesor` | Académico (`/api/auth/login`) | Cursos asignados, tomar asistencia, crear estudiantes |
| `administrador` | Administrativo (`/api/auth/admin/login`) | Gestión global de usuarios, cursos, auditoría |

No existe `superadmin` ni `admin` como rol. El valor en BD y JWT es siempre `administrador`.

## Estructura

```
monitor_asistencia_ia/
├── backend/          # FastAPI
│   ├── app/api/      # auth, users, admin_*, attendance, face_auth, cursos
│   ├── app/core/     # security, config
│   ├── app/db/       # database, models, repositories
│   ├── app/services/ # auth, face, attendance, camera, liveness
│   └── scripts/create_admin.py
├── frontend/         # login dual + paneles por rol
├── ai/face/          # detección, embeddings, liveness, cámara
├── database/mysql/   # schema + seed (roles unificados)
└── docs/
```

## Puesta en marcha rápida

1. Crear BD MySQL y usuario de aplicación.
2. Ejecutar `database/mysql/01_schema.sql` y `02_seed.sql`.
3. Copiar `.env.example` → `.env` y completar credenciales + `JWT_SECRET_KEY`.
4. Entorno virtual e instalar:
   ```bash
   python -m venv .venv
   # Windows: .\.venv\Scripts\Activate.ps1
   pip install -r requirements-base.txt
   # Opcional IA: pip install -r requirements-ai.txt
   ```
5. Backend:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```
6. Swagger: http://127.0.0.1:8000/docs  
7. Frontend: abrir con Live Server (puerto 5500) o servir estáticos.

### Usuarios demo (seed)

Tras ejecutar el seed, la contraseña hash del seed debe corresponder a la usada al generar `@hash` en el SQL (revisar el script). Usuario administrador demo: `admin` / según hash del seed.

Crear admin controlado:
```bash
cd backend
PYTHONPATH=. python scripts/create_admin.py
```

## Endpoints clave

### Persona 1 – Auth / Usuarios
- `POST /api/auth/login` — profesor y estudiante
- `POST /api/auth/admin/login` — solo administrador
- `POST /api/auth/face-login` — login facial
- `POST /api/auth/register-profesor` — queda `pendiente`
- `POST /api/admin/usuarios` — admin crea estudiante/profesor
- `GET  /api/admin/auditoria/...` — auditoría

### Persona 2 – Asistencia / Cámara
- `GET  /api/attendance/health`
- `POST /api/attendance/check-in`
- `POST /api/attendance/camera/check-in`
- `POST /api/attendance/camera/reset`

## División de tareas (visible en el código)

- Comentarios en `main.py`, `auth.py`, `attendance.py`, servicios y schemas.
- Aunque el desarrollo interno pueda ser de una persona, se respeta la división original del equipo.

## Notas

- No inventar métricas del modelo ML.
- Chatbot y ML (Persona 3 y 4) se integran en fases posteriores.
- Seguir el Manual Técnico MySQL para política de chatbot, reportes y esquema canónico a largo plazo.


## Persona 3 — Analytics y predicciones (integrado)

| Método | Ruta | Roles |
|--------|------|--------|
| GET | `/api/analytics/me` | autenticado |
| GET | `/api/analytics/estudiante/{usuario_id}` | profesor, administrador |
| GET | `/api/analytics/curso/{curso_id}` | profesor, administrador |
| GET | `/api/analytics/global` | administrador |
| GET | `/api/predictions/me` | autenticado |
| GET | `/api/predictions/estudiante/{usuario_id}` | profesor, administrador |
| POST | `/api/predictions/train` | administrador |
| POST | `/api/predictions/evaluate` | administrador |

Documentación del modelo: `docs/modelo_ml.md`.  
Paquete ML: `ai/ml/` (features, train, predict, evaluate).

Las predicciones se presentan siempre como **estimación**, no como certeza.  
No se inventan métricas: accuracy/F1/etc. solo las calculadas en train/evaluate.


## Persona 4 (Jakelin) — Chatbot y frontend

- UI: `frontend/components/chatbot/`, `frontend/assets/js/chatbot.js`, `frontend/assets/css/chatbot.css`
- Dashboards: `frontend/estudiante/`, `frontend/profesor/`, `frontend/administrador/`
- API: `POST /api/chatbot/message` (JWT + policy MySQL)
- Servicios: `chatbot_policy_service`, `chatbot_data_service`
- Roles en API: `estudiante` | `profesor` | `administrador`
- **Sin registro público** (Manual §3.1). Sin Supabase.

Cliente: `frontend/assets/js/api.js` + `auth.js` (AsistenciaAuth + Auth).
