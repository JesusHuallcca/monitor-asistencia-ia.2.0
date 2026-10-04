document.addEventListener("DOMContentLoaded", async () => {
  const role = document.body.dataset.createRole || "ESTUDIANTE";
  const allowed = role === "PROFESOR" ? ["ADMINISTRADOR"] : ["ADMINISTRADOR", "PROFESOR"];
  const current = await AsistenciaAuth.protectPage(allowed);
  if (!current) return;
  const form = document.getElementById("createUserForm");
  const msg = document.getElementById("formMessage");
  form?.addEventListener("submit", async (e) => {
    e.preventDefault(); msg.className="form-message"; msg.textContent="Guardando...";
    const f = new FormData(form);
    const payload = {nombres:f.get("nombres"),apellidos:f.get("apellidos"),email:f.get("email"),password:f.get("password"),rol:role};
    if(role==="ESTUDIANTE") Object.assign(payload,{codigo_estudiante:f.get("codigo"),carrera:f.get("detalle"),ciclo:f.get("ciclo")||null});
    else Object.assign(payload,{codigo_profesor:f.get("codigo"),especialidad:f.get("detalle")});
    try { const data=await apiRequest("/api/users/create",{method:"POST",body:JSON.stringify(payload)}); msg.className="form-message success"; msg.textContent=data.message; form.reset(); }
    catch(err){ msg.className="form-message error"; msg.textContent=err.message; }
  });
});
