document.addEventListener("DOMContentLoaded", async () => {
  const user = await AsistenciaAuth.protectPage(["ADMINISTRADOR"], "../login/admin_login.html");
  if (!user && window.location.protocol !== "file:" && !window.location.search.includes("demo=true")) return;

  document.getElementById("logoutAdmin")?.addEventListener("click", AsistenciaAuth.logoutUser);

  // ==========================================
  // 1. CARGA DE MÉTRICAS DEL SERVIDOR
  // ==========================================
  try {
    const data = await apiRequest("/api/admin/dashboard");
    const r = data.resumen || {};
    const a = data.asistencia || {};

    setText("metricUsuarios", r.usuarios ?? 6);
    setText("metricEstudiantes", r.estudiantes ?? 3);
    setText("metricProfesores", r.profesores ?? 2);
    setText("metricCursos", r.cursos ?? 4);
    setText("metricPromedio", `${a.promedio ?? 89}%`);
    setText("metricAusencias", `${a.tasa_ausencia ?? 6}%`);
    setText("metricTardanzas", `${a.tasa_tardanza ?? 5}%`);
    setText("formulaMediaValue", `${a.promedio ?? 89}%`);

    const totalRoles = Math.max(r.usuarios || 6, 1);
    const nEst = r.estudiantes ?? 3;
    const nProf = r.profesores ?? 2;
    const nAdmin = r.administradores ?? 1;

    setBar("barEstudiantes", (nEst / totalRoles) * 100, nEst);
    setBar("barProfesores", (nProf / totalRoles) * 100, nProf);
    setBar("barAdministradores", (nAdmin / totalRoles) * 100, nAdmin);

    renderSessions(data.sesiones_recientes || []);
  } catch (error) {
    console.warn("Servidor no disponible o modo demo activo:", error.message);
  }

  // ==========================================
  // CARGA DINÁMICA DE USUARIOS Y CURSOS DESDE BD
  // ==========================================
  async function loadUsersFromDb() {
    try {
      const users = await apiRequest("/api/admin/users");
      if (Array.isArray(users) && users.length > 0) {
        const tbody = document.querySelector("#adminUsersTable tbody");
        if (tbody) {
          tbody.innerHTML = users.map((u) => {
            const roleLower = String(u.rol || "estudiante").toLowerCase();
            const prettyRole = roleLower.charAt(0).toUpperCase() + roleLower.slice(1);
            return `
              <tr data-role="${roleLower}" data-status="activo">
                <td><strong>${u.nombres || ""} ${u.apellidos || ""}</strong></td>
                <td>${u.correo || "-"}</td>
                <td><span class="badge-role ${roleLower}">${prettyRole}</span></td>
                <td>${u.id_usuario ? `USR-${String(u.id_usuario).padStart(3, '0')}` : "-"}</td>
                <td><span class="status-badge activo"><i class="fa-solid fa-circle-check"></i> Activo</span></td>
                <td style="text-align:right">
                  <button class="admin-btn admin-btn-outline admin-btn-sm" title="Editar"><i class="fa-solid fa-pen"></i></button>
                </td>
              </tr>
            `;
          }).join("");
          const userCountEl = document.getElementById("adminUserCount");
          if (userCountEl) {
            userCountEl.textContent = `${users.length} usuarios registrados`;
          }
        }
      }
    } catch (e) {
      console.warn("No se pudieron cargar usuarios de la BD, manteniendo datos demo:", e.message);
    }
  }

  async function loadCoursesFromDb() {
    try {
      const courses = await apiRequest("/api/courses/");
      if (Array.isArray(courses) && courses.length > 0) {
        const tbody = document.querySelector("#adminCoursesTable tbody");
        if (tbody) {
          tbody.innerHTML = courses.map((c) => `
            <tr>
              <td><strong>${c.codigo || "CURSO"}</strong></td>
              <td>${c.nombre || "Sin nombre"}</td>
              <td>Sec ${c.seccion || "A"} (${c.modalidad || "Presencial"})</td>
              <td>Docente Titular</td>
              <td>${c.aula || "Aula"}</td>
              <td><strong>28</strong> estudiantes</td>
              <td><span class="status-badge activo">Dictando</span></td>
              <td style="text-align:right"><button class="admin-btn admin-btn-outline admin-btn-sm" title="Ver detalles"><i class="fa-solid fa-eye"></i></button></td>
            </tr>
          `).join("");
        }
      }
    } catch (e) {
      console.warn("No se pudieron cargar cursos de la BD, manteniendo datos demo:", e.message);
    }
  }

  // Ejecutar carga de datos reales
  loadUsersFromDb();
  loadCoursesFromDb();

  // ==========================================
  // 2. NAVEGACIÓN SPA DEL SIDEBAR DE ADMIN
  // ==========================================
  const menuLinks = document.querySelectorAll(".admin-menu a[data-section]");
  const sections = document.querySelectorAll(".admin-section");

  function navigateAdminSection(sectionId) {
    if (!sectionId) return;

    sections.forEach((s) => {
      s.style.display = "none";
      s.classList.remove("active");
    });

    const target = document.getElementById(`section-${sectionId}`) ||
                   document.querySelector(`.admin-section[data-section="${sectionId}"]`);

    if (target) {
      target.style.display = "";
      target.classList.add("active");
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    menuLinks.forEach((l) => {
      if (l.dataset.section === sectionId) {
        l.classList.add("active");
      } else {
        l.classList.remove("active");
      }
    });
  }

  menuLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const sec = link.dataset.section;
      if (sec) {
        navigateAdminSection(sec);
        try {
          history.replaceState(null, "", `#${sec}`);
        } catch (_) {}
      }
    });
  });

  const currentHash = window.location.hash.replace("#", "").trim();
  if (currentHash) {
    navigateAdminSection(currentHash);
  }

  // ==========================================
  // 3. FILTRO DE USUARIOS (EN VIVO)
  // ==========================================
  const userSearch = document.getElementById("adminUserSearch");
  const userRoleFilter = document.getElementById("adminUserRoleFilter");
  const userStatusFilter = document.getElementById("adminUserStatusFilter");
  const userRows = document.querySelectorAll("#adminUsersTable tbody tr");
  const userCount = document.getElementById("adminUserCount");

  function filterUsers() {
    const query = userSearch ? userSearch.value.toLowerCase().trim() : "";
    const role = userRoleFilter ? userRoleFilter.value : "todos";
    const status = userStatusFilter ? userStatusFilter.value : "todos";

    let visible = 0;
    userRows.forEach((row) => {
      const text = row.innerText.toLowerCase();
      const rowRole = row.dataset.role || "";
      const rowStatus = row.dataset.status || "";

      const matchQuery = !query || text.includes(query);
      const matchRole = role === "todos" || rowRole === role;
      const matchStatus = status === "todos" || rowStatus === status;

      if (matchQuery && matchRole && matchStatus) {
        row.style.display = "";
        visible++;
      } else {
        row.style.display = "none";
      }
    });

    if (userCount) {
      userCount.textContent = `${visible} usuarios encontrados`;
    }
  }

  userSearch?.addEventListener("input", filterUsers);
  userRoleFilter?.addEventListener("change", filterUsers);
  userStatusFilter?.addEventListener("change", filterUsers);

  // ==========================================
  // 4. FILTRO DE CURSOS (EN VIVO)
  // ==========================================
  const courseSearch = document.getElementById("adminCourseSearch");
  const courseRows = document.querySelectorAll("#adminCoursesTable tbody tr");

  courseSearch?.addEventListener("input", () => {
    const query = courseSearch.value.toLowerCase().trim();
    courseRows.forEach((row) => {
      const match = !query || row.innerText.toLowerCase().includes(query);
      row.style.display = match ? "" : "none";
    });
  });

  // ==========================================
  // 5. BUSCADOR GLOBAL DEL TOPBAR
  // ==========================================
  const globalAdminSearch = document.getElementById("globalAdminSearch");
  globalAdminSearch?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const val = globalAdminSearch.value.trim().toLowerCase();
      if (!val) return;
      // Navegar a usuarios y aplicar filtro
      navigateAdminSection("usuarios");
      if (userSearch) {
        userSearch.value = val;
        filterUsers();
      }
    }
  });

});

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function setBar(id, percent, count) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.width = `${Math.min(Math.max(percent, 0), 100)}%`;
  const strong = el.parentElement?.parentElement?.querySelector("strong");
  if (strong) strong.textContent = count;
}

function renderSessions(sessions) {
  const container = document.getElementById("recentSessions");
  if (!container) return;

  if (!sessions.length) {
    container.innerHTML = `
      <div class="session-row">
        <div class="session-icon"><i class="fa-regular fa-calendar-check"></i></div>
        <div class="session-info">
          <strong>Inteligencia Artificial Aplicada</strong>
          <span>IA-301 · Hoy · 08:00 - 10:00</span>
        </div>
        <span class="status-pill activa">Activa</span>
      </div>
      <div class="session-row">
        <div class="session-icon"><i class="fa-regular fa-calendar-check"></i></div>
        <div class="session-info">
          <strong>Visión por Computador y Reconocimiento</strong>
          <span>VIS-402 · Ayer · 10:00 - 12:00</span>
        </div>
        <span class="status-pill cerrada">Cerrada</span>
      </div>`;
    return;
  }

  container.innerHTML = sessions.map((s) => {
    const course = s.cursos || {};
    return `
      <div class="session-row">
        <div class="session-icon"><i class="fa-regular fa-calendar-check"></i></div>
        <div class="session-info">
          <strong>${course.nombre || "Curso"}</strong>
          <span>${course.codigo || ""} · ${s.fecha || ""} · ${s.hora_inicio || ""}</span>
        </div>
        <span class="status-pill ${String(s.estado || "").toLowerCase()}">${s.estado || "-"}</span>
      </div>`;
  }).join("");
}
