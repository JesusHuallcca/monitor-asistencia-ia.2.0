"""
Pruebas de Generación de Reportes Excel y PDF.
Fase 8: Hardening y Calidad.
"""

def test_profesor_descarga_reporte_excel(client, profesor_headers):
    """Verifica la descarga exitosa de un archivo Excel de asistencia."""
    payload = {"id_curso": 1, "formato": "XLSX"}
    response = client.post("/api/reports/attendance", json=payload, headers=profesor_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(response.content) > 500


def test_profesor_descarga_reporte_pdf(client, profesor_headers):
    """Verifica la descarga exitosa de un archivo PDF de asistencia."""
    payload = {"id_curso": 1, "formato": "PDF"}
    response = client.post("/api/reports/attendance", json=payload, headers=profesor_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 500


def test_reporte_formato_invalido(client, profesor_headers):
    """Verifica error 422 si se solicita un formato no soportado (ej. CSV o WORD)."""
    payload = {"id_curso": 1, "formato": "DOCX"}
    response = client.post("/api/reports/attendance", json=payload, headers=profesor_headers)
    assert response.status_code == 422
