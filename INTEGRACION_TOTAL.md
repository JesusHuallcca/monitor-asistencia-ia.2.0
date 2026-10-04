# Monitor Inteligente de Asistencia IA - Integración total

Esta carpeta consolida el proyecto principal con los aportes de las ramas de autenticación y asistencia/IA, manteniendo Supabase como base de datos y autenticación.

## Qué quedó integrado

- Frontend por rol: estudiante, profesor y administrador.
- Login académico y login administrador separados, con CSS independiente.
- FastAPI + Supabase Auth + perfiles por rol.
- Regla de creación: ADMINISTRADOR crea profesores y estudiantes; PROFESOR solo estudiantes; ESTUDIANTE no crea cuentas.
- Cursos con lectura filtrada por rol.
- Asistencia con lectura propia para estudiante y control de curso para profesor.
- Analítica base.
- Chatbot global con JWT y restricciones por rol.
- Código de reconocimiento facial/IA de la rama de asistencia conservado en `ai/` y sus fuentes originales en `integracion_fuentes/` para la siguiente conexión a Supabase.
- Script completo de Supabase: `database/supabase_complete_setup.sql`.

## Arranque

1. En Supabase SQL Editor ejecute `database/supabase_complete_setup.sql` (si ya tiene tablas, revise primero; usa `if not exists` para tablas).
2. Copie `backend/.env.example` a `backend/.env` y coloque URL, publishable key y secret key.
3. Cree un entorno virtual limpio (no se incluye `.venv` en el ZIP).
4. Instale: `python -m pip install -r backend/requirements.txt`.
5. Desde `backend`: `python -m uvicorn app.main:app --reload`.
6. Abra `http://127.0.0.1:8000/docs` y pruebe `/api/test-supabase`.
7. Ejecute el frontend con Live Server.

## Seguridad

El chatbot y los endpoints no aceptan un rol enviado por el navegador: obtienen el usuario desde el JWT de Supabase. El estudiante solo consulta su información; el profesor se limita a sus cursos/alumnos; el administrador tiene visión global autorizada. La secret key de Supabase se usa únicamente en FastAPI.

## IA facial

Los archivos de IA provenientes de la rama de asistencia fueron integrados como código fuente, pero no se fuerza todavía su persistencia en Supabase para no mezclar el repositorio MySQL anterior con el esquema actual. La siguiente fase es adaptar `face_repository` a `datos_faciales` y registrar resultados en `asistencias`.
