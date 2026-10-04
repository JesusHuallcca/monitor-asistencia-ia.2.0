document.addEventListener("DOMContentLoaded", () => {
  const startButton = document.getElementById("startCameraButton");
  const video = document.getElementById("faceVideo");
  const placeholder = document.getElementById("cameraPlaceholder");
  const status = document.getElementById("faceStatus");
  const frame = document.getElementById("framePercent");

  startButton?.addEventListener("click", async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
      video.srcObject = stream;
      video.style.display = "block";
      placeholder.style.display = "none";
      status.textContent = "Cámara activa";
      frame.textContent = "100%";
      startButton.querySelector("span").textContent = "Cámara iniciada";
    } catch (error) {
      console.error(error);
      status.textContent = "Sin permiso";
      frame.textContent = "0%";
      alert("No se pudo acceder a la cámara. Revisa los permisos del navegador.");
    }
  });
});
