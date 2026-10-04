document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("registerForm");
  const messageBox = document.getElementById("registerMessage");
  const submitButton = document.getElementById("registerSubmit");
  const studentFields = document.getElementById("studentFields");
  const teacherFields = document.getElementById("teacherFields");
  const roleInputs = document.querySelectorAll('input[name="rol"]');

  function currentRole() {
    return document.querySelector('input[name="rol"]:checked')?.value || "ESTUDIANTE";
  }

  function updateRoleFields() {
    const role = currentRole();
    studentFields.classList.toggle("hidden", role !== "ESTUDIANTE");
    teacherFields.classList.toggle("hidden", role !== "PROFESOR");

    document.getElementById("codigoEstudiante").required = role === "ESTUDIANTE";
    document.getElementById("carrera").required = role === "ESTUDIANTE";
    document.getElementById("codigoProfesor").required = role === "PROFESOR";
    document.getElementById("especialidad").required = role === "PROFESOR";
  }

  roleInputs.forEach((input) => input.addEventListener("change", updateRoleFields));
  updateRoleFields();

  function showMessage(text, success = false) {
    messageBox.textContent = text;
    messageBox.classList.add("show");
    messageBox.classList.toggle("success", success);
  }

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    messageBox.classList.remove("show", "success");

    const rol = currentRole();
    const email = document.getElementById("registerEmail").value.trim();
    const password = document.getElementById("registerPassword").value;

    const payload = {
      nombres: document.getElementById("nombres").value.trim(),
      apellidos: document.getElementById("apellidos").value.trim(),
      email,
      password,
      rol,
      codigo_estudiante: rol === "ESTUDIANTE" ? document.getElementById("codigoEstudiante").value.trim() : null,
      carrera: rol === "ESTUDIANTE" ? document.getElementById("carrera").value.trim() : null,
      ciclo: rol === "ESTUDIANTE" ? document.getElementById("ciclo").value.trim() : null,
      codigo_profesor: rol === "PROFESOR" ? document.getElementById("codigoProfesor").value.trim() : null,
      especialidad: rol === "PROFESOR" ? document.getElementById("especialidad").value.trim() : null,
    };

    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Creando cuenta...';

    try {
      await apiRequest("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      showMessage("Cuenta creada correctamente. Iniciando sesión...", true);

      const data = await AsistenciaAuth.loginUser(email, password);
      setTimeout(() => AsistenciaAuth.redirectByRole(data.profile?.rol), 550);
    } catch (error) {
      showMessage(error.message || "No se pudo crear la cuenta.");
    } finally {
      submitButton.disabled = false;
      submitButton.innerHTML = '<span>Crear cuenta</span><i class="fa-solid fa-arrow-right"></i>';
    }
  });
});
