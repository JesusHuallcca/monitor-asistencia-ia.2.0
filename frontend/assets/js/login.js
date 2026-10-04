document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const errorBox = document.getElementById("loginError");
  const submitButton = document.getElementById("loginSubmit");
  const passwordInput = document.getElementById("password");
  const togglePassword = document.getElementById("togglePassword");
  const mode = document.body.dataset.loginMode || "academic";

  togglePassword?.addEventListener("click", () => {
    const nextType = passwordInput.type === "password" ? "text" : "password";
    passwordInput.type = nextType;
    togglePassword.innerHTML = nextType === "password"
      ? '<i class="fa-regular fa-eye-slash"></i>'
      : '<i class="fa-regular fa-eye"></i>';
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorBox.textContent = "";
    errorBox.classList.remove("show");

    const email = document.getElementById("email").value.trim();
    const password = passwordInput.value;

    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Ingresando...';

    try {
      const data = await AsistenciaAuth.loginUser(email, password);
      const role = data.rol || data.profile?.rol;

      if (mode === "admin" && role !== "ADMINISTRADOR") {
        AsistenciaAuth.clearSession();
        throw new Error("Este acceso es exclusivo para administradores.");
      }

      if (mode === "academic" && role === "ADMINISTRADOR") {
        AsistenciaAuth.clearSession();
        throw new Error("Los administradores deben usar el Portal Administrativo.");
      }

      AsistenciaAuth.redirectByRole(role);
    } catch (error) {
      errorBox.textContent = error.message || "No se pudo iniciar sesión.";
      errorBox.classList.add("show");
    } finally {
      submitButton.disabled = false;
      submitButton.innerHTML = 'Iniciar sesión <i class="fa-solid fa-arrow-right"></i>';
    }
  });
});
