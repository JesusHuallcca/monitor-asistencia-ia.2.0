"""
Pruebas de Seguridad y Control de Acceso basado en Roles (RBAC).
Fase 8: Hardening y Calidad.
"""

def test_estudiante_no_puede_crear_usuarios(client, estudiante_headers):
    """Verifica que un estudiante reciba 403 Forbidden al intentar crear usuarios."""
    payload = {
        "nombres": "Falso",
        "apellidos": "Usuario",
        "correo": "falso@institucion.edu.pe",
        "password": "Password123!",
        "rol": "ESTUDIANTE",
        "codigo_estudiante": "EST-99999"
    }
    response = client.post("/api/users/create", json=payload, headers=estudiante_headers)
    assert response.status_code == 403


def test_estudiante_no_puede_generar_reportes(client, estudiante_headers):
    """Verifica que un estudiante reciba 403 Forbidden al solicitar reportes institucionales."""
    payload = {
        "id_curso": 1,
        "formato": "XLSX"
    }
    response = client.post("/api/reports/attendance", json=payload, headers=estudiante_headers)
    assert response.status_code == 403


def test_admin_acceso_dashboard(client, admin_headers):
    """Verifica que un administrador acceda correctamente al resumen del dashboard."""
    response = client.get("/api/admin/dashboard", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
