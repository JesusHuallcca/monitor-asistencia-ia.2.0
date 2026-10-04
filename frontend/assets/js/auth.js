function saveSession(data) {
  localStorage.setItem("asistencia_access_token", data.access_token);
  localStorage.setItem("asistencia_refresh_token", data.refresh_token || "");
  // Guardar perfil con todos los campos que necesita el chatbot y otras vistas
  const profile = data.profile || {};
  const mergedProfile = {
    ...profile,
    rol: data.rol || profile.rol || "ESTUDIANTE",
    nombres: data.nombres || profile.nombres || "",
    apellidos: data.apellidos || profile.apellidos || "",
    id: data.id_usuario || profile.id || null,
  };
  localStorage.setItem("asistencia_profile", JSON.stringify(mergedProfile));
}

function clearSession() {
  localStorage.removeItem("asistencia_access_token");
  localStorage.removeItem("asistencia_refresh_token");
  localStorage.removeItem("asistencia_profile");
}

function getStoredProfile() {
  try {
    return JSON.parse(localStorage.getItem("asistencia_profile") || "{}");
  } catch (_) {
    return {};
  }
}

function redirectByRole(role) {
  if (role === "ADMINISTRADOR") {
    window.location.href = "../administrador/dashboard.html";
    return;
  }
  if (role === "PROFESOR") {
    window.location.href = "../profesor/dashboard.html";
    return;
  }
  window.location.href = "../estudiante/dashboard.html";
}

async function loginUser(email, password) {
  const data = await apiRequest("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ correo: email, password }),
  });
  saveSession(data);
  return data;
}

async function getCurrentUser() {
  return apiRequest("/api/auth/me");
}

async function protectPage(allowedRoles = [], loginPath = "../login/portal_login.html") {
  const token = localStorage.getItem("asistencia_access_token");
  const isLocalFile = window.location.protocol === "file:" || window.location.search.includes("demo=true");

  if (!token) {
    if (isLocalFile) {
      console.warn("Modo demostración o vista previa local activo.");
      return { rol: allowedRoles[0] || "ESTUDIANTE", nombres: "Usuario", apellidos: "Demo" };
    }
    window.location.href = loginPath;
    return null;
  }

  try {
    const user = await getCurrentUser();
    if (allowedRoles.length && !allowedRoles.includes(user.rol)) {
      redirectByRole(user.rol);
      return null;
    }

    const nameTargets = document.querySelectorAll("[data-auth-name]");
    nameTargets.forEach((el) => {
      el.textContent = `${user.nombres} ${user.apellidos}`.trim();
    });

    const roleTargets = document.querySelectorAll("[data-auth-role]");
    roleTargets.forEach((el) => {
      const pretty = user.rol.charAt(0) + user.rol.slice(1).toLowerCase();
      el.textContent = pretty;
    });

    return user;
  } catch (error) {
    console.warn("No se pudo validar sesión con el servidor:", error);
    const stored = getStoredProfile();
    if (stored && stored.rol && (!allowedRoles.length || allowedRoles.includes(stored.rol))) {
      return stored;
    }
    if (isLocalFile) {
      return { rol: allowedRoles[0] || "ESTUDIANTE", nombres: "Usuario", apellidos: "Demo" };
    }
    clearSession();
    window.location.href = loginPath;
    return null;
  }
}

function logoutUser(event) {
  if (event) event.preventDefault();
  clearSession();
  window.location.href = "../login/portal_login.html";
}

window.AsistenciaAuth = {
  loginUser,
  logoutUser,
  protectPage,
  getCurrentUser,
  getStoredProfile,
  redirectByRole,
  clearSession,
};
