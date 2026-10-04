"""Generación de reportes Excel (XLSX) y PDF (Fase 4)."""

import io
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth_dependencies import CurrentUser
from app.models import Asistencia, SesionAsistencia, Matricula, ReporteGenerado

router = APIRouter(prefix="/api/reports", tags=["Reportes"])


class ReportRequest(BaseModel):
    id_curso: int
    formato: str = "XLSX"  # XLSX | PDF


@router.post("/attendance")
def generate_attendance_report(
    payload: ReportRequest,
    current: CurrentUser,
    db: Session = Depends(get_db),
):
    if current.rol not in ("PROFESOR", "ADMINISTRADOR"):
        raise HTTPException(403, detail="Solo profesor o administrador puede generar reportes.")
    if payload.formato not in ("XLSX", "PDF"):
        raise HTTPException(422, detail="Formato inválido. Use XLSX o PDF.")

    from app.core.audit import log_audit_event
    log_audit_event(
        db=db,
        user_id=current.id_usuario,
        accion="GENERAR_REPORTE",
        entidad="cursos",
        entidad_id=str(payload.id_curso),
        detalle={"formato": payload.formato, "id_curso": payload.id_curso},
    )

    try:
        nuevo_rep = ReporteGenerado(
            id_usuario=current.id_usuario,
            tipo="ASISTENCIA",
            formato=payload.formato,
            filtros={"id_curso": payload.id_curso},
        )
        db.add(nuevo_rep)
        db.commit()
    except Exception:
        db.rollback()

    # Obtener sesiones del curso
    sesion_ids = [
        s.id_sesion for s in db.query(SesionAsistencia).filter(
            SesionAsistencia.id_curso == payload.id_curso
        ).all()
    ]
    matriculas = db.query(Matricula).filter(
        Matricula.id_curso == payload.id_curso, Matricula.estado == True
    ).all()

    rows = []
    for mat in matriculas:
        est = mat.estudiante
        for sid in sesion_ids:
            asis = db.query(Asistencia).filter(
                Asistencia.id_sesion == sid,
                Asistencia.id_estudiante == est.id_estudiante,
            ).first()
            sesion = db.query(SesionAsistencia).filter(SesionAsistencia.id_sesion == sid).first()
            rows.append({
                "Estudiante": f"{est.usuario.nombres} {est.usuario.apellidos}",
                "Código": est.codigo_estudiante,
                "Fecha": str(sesion.fecha) if sesion else "",
                "Estado": asis.estado if asis else "AUSENTE",
                "Método": asis.metodo_registro if asis else "—",
            })

    if payload.formato == "XLSX":
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Asistencias"
        headers = ["Estudiante", "Código", "Fecha", "Estado", "Método"]
        ws.append(headers)
        for row in rows:
            ws.append([row[h] for h in headers])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        filename = f"asistencia_curso_{payload.id_curso}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return StreamingResponse(
            buf,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    else:  # PDF
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [Paragraph(f"Reporte de Asistencias – Curso #{payload.id_curso}", styles["Title"])]
        table_data = [["Estudiante", "Código", "Fecha", "Estado", "Método"]]
        for row in rows:
            table_data.append([row["Estudiante"], row["Código"], row["Fecha"], row["Estado"], row["Método"]])
        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a73e8")),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
            ("GRID",       (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE",   (0, 0), (-1, -1), 8),
        ]))
        elements.append(t)
        doc.build(elements)
        buf.seek(0)
        filename = f"asistencia_curso_{payload.id_curso}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return StreamingResponse(
            buf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
