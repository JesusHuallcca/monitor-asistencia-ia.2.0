/**
 * reports.js — Descarga real de reportes Excel (XLSX) y PDF
 * Llama a POST /api/reports/attendance con autenticación JWT.
 * Se incluye en el dashboard del Profesor y del Administrador.
 * v1.0 — Monitor Asistencia IA (MySQL)
 */

(function () {
  "use strict";

  const API_BASE = "http://127.0.0.1:8000";

  /**
   * Descarga un reporte de asistencia para un curso dado.
   * @param {number|string} idCurso  — ID del curso en la BD
   * @param {'XLSX'|'PDF'}  formato  — formato de descarga
   * @param {HTMLElement}   [btn]    — botón que activó la acción (para feedback visual)
   */
  async function descargarReporte(idCurso, formato, btn) {
    const token = localStorage.getItem("access_token");

    if (!token) {
      _toast("⚠️ Inicia sesión primero para descargar reportes.", "warning");
      return;
    }

    if (!idCurso) {
      _toast("⚠️ Selecciona un curso antes de descargar el reporte.", "warning");
      return;
    }

    // Feedback visual en el botón
    const textoOriginal = btn ? btn.innerHTML : "";
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generando...`;
    }

    try {
      const resp = await fetch(`${API_BASE}/api/reports/attendance`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ id_curso: Number(idCurso), formato }),
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || `Error ${resp.status}`);
      }

      // Extraer nombre de archivo del encabezado Content-Disposition
      const disposition = resp.headers.get("Content-Disposition") || "";
      let filename = formato === "XLSX"
        ? `reporte_asistencia_curso${idCurso}.xlsx`
        : `reporte_asistencia_curso${idCurso}.pdf`;

      const match = disposition.match(/filename=([^;]+)/);
      if (match) filename = match[1].replace(/"/g, "").trim();

      // Descargar como blob
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 200);

      _toast(
        `✅ Reporte ${formato} descargado: ${filename}`,
        "success"
      );
    } catch (error) {
      console.error("[Reports] Error al descargar reporte:", error);
      _toast(`❌ ${error.message}`, "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = textoOriginal;
      }
    }
  }

  /**
   * Muestra un toast de notificación temporal.
   */
  function _toast(msg, tipo = "info") {
    // Si existe un contenedor de toast, usarlo; si no, crear uno
    let container = document.getElementById("reportToastContainer");
    if (!container) {
      container = document.createElement("div");
      container.id = "reportToastContainer";
      container.style.cssText = `
        position: fixed; bottom: 24px; right: 24px; z-index: 99999;
        display: flex; flex-direction: column; gap: 10px; align-items: flex-end;
      `;
      document.body.appendChild(container);
    }

    const colors = {
      success: { bg: "#dcfce7", border: "#16a34a", text: "#15803d" },
      error: { bg: "#fee2e2", border: "#dc2626", text: "#b91c1c" },
      warning: { bg: "#fef3c7", border: "#d97706", text: "#b45309" },
      info: { bg: "#dbeafe", border: "#2563eb", text: "#1d4ed8" },
    };
    const c = colors[tipo] || colors.info;

    const toast = document.createElement("div");
    toast.style.cssText = `
      background: ${c.bg}; border: 1px solid ${c.border}; color: ${c.text};
      padding: 12px 18px; border-radius: 10px; font-size: 13px; font-weight: 600;
      box-shadow: 0 4px 16px rgba(0,0,0,.12); max-width: 340px;
      animation: toastIn .25s ease; pointer-events: none;
    `;
    toast.textContent = msg;

    // Animación CSS inline
    if (!document.getElementById("reportToastStyle")) {
      const style = document.createElement("style");
      style.id = "reportToastStyle";
      style.textContent = `
        @keyframes toastIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
        @keyframes toastOut { from { opacity:1; } to { opacity:0; } }
      `;
      document.head.appendChild(style);
    }

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = "toastOut .3s ease forwards";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  /**
   * Obtiene la lista de cursos disponibles vía API y puebla un <select>.
   * @param {string} selectId — ID del elemento <select> a poblar
   */
  async function poblarSelectCursos(selectId) {
    const token = localStorage.getItem("access_token");
    const sel = document.getElementById(selectId);
    if (!sel) return;

    sel.innerHTML = '<option value="">Cargando cursos...</option>';

    try {
      const resp = await fetch(`${API_BASE}/api/courses/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!resp.ok) throw new Error("No se pudieron cargar los cursos");
      const cursos = await resp.json();

      sel.innerHTML = '<option value="">— Selecciona un curso —</option>';
      (Array.isArray(cursos) ? cursos : cursos.items || []).forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.id_curso;
        opt.textContent = `${c.nombre} (ID ${c.id_curso})`;
        sel.appendChild(opt);
      });
    } catch (e) {
      sel.innerHTML =
        '<option value="">Sin cursos disponibles (API offline)</option>';
      console.warn("[Reports] No se cargaron cursos:", e.message);
    }
  }

  // ──────────────────────────────────────────────
  // Inicialización automática cuando el DOM carga
  // ──────────────────────────────────────────────
  function _init() {
    // Poblar selectores de cursos si existen en la página
    poblarSelectCursos("reportCursoSelectProf");
    poblarSelectCursos("reportCursoSelectAdmin");

    // Botones del Profesor
    const btnProfXlsx = document.getElementById("btnDescargaXlsxProf");
    const btnProfPdf  = document.getElementById("btnDescargaPdfProf");

    if (btnProfXlsx) {
      btnProfXlsx.addEventListener("click", () => {
        const id = document.getElementById("reportCursoSelectProf")?.value;
        descargarReporte(id, "XLSX", btnProfXlsx);
      });
    }
    if (btnProfPdf) {
      btnProfPdf.addEventListener("click", () => {
        const id = document.getElementById("reportCursoSelectProf")?.value;
        descargarReporte(id, "PDF", btnProfPdf);
      });
    }

    // Botones del Administrador
    const btnAdminXlsx = document.getElementById("btnDescargaXlsxAdmin");
    const btnAdminPdf  = document.getElementById("btnDescargaPdfAdmin");

    if (btnAdminXlsx) {
      btnAdminXlsx.addEventListener("click", () => {
        const id = document.getElementById("reportCursoSelectAdmin")?.value;
        descargarReporte(id, "XLSX", btnAdminXlsx);
      });
    }
    if (btnAdminPdf) {
      btnAdminPdf.addEventListener("click", () => {
        const id = document.getElementById("reportCursoSelectAdmin")?.value;
        descargarReporte(id, "PDF", btnAdminPdf);
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", _init);
  } else {
    _init();
  }

  // Exponer API pública por si se necesita invocar desde consola o ChatBot
  window.AsistenciaReports = { descargarReporte, poblarSelectCursos };
})();
