"""
Pruebas unitarias de Autenticación y JWT.
Fase 8: Hardening y Calidad.
"""

def test_health_check(client):
    """Verifica que el endpoint de salud responda 200 y confirme estado saludable."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "ok"


def test_login_exitoso(client):
    """Verifica login correcto con usuario de prueba y recepción de token JWT."""
    payload = {
        "correo": "profesor1@asistencia.local",
        "password": "admin123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["rol"] == "PROFESOR"


def test_login_credenciales_invalidas(client):
    """Verifica rechazo con 401 para contraseñas o correos incorrectos."""
    payload = {
        "correo": "profesor1@asistencia.local",
        "password": "password_incorrecto_123"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "detail" in response.json()


def test_login_sin_correo(client):
    """Verifica error de validación 422 si falta el campo de correo."""
    payload = {"password": "admin123"}
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 422


def test_me_endpoint_autenticado(client, profesor_headers):
    """Verifica consulta de datos propios con token válido."""
    response = client.get("/api/auth/me", headers=profesor_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["rol"] == "PROFESOR"


def test_me_endpoint_sin_token(client):
    """Verifica 401 Unauthorized si se omite la cabecera Authorization."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
