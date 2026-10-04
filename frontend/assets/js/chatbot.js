// =========================================================
// ASISTENCIA IA - CHATBOT GLOBAL
// Compartido por:
// ESTUDIANTE | PROFESOR | ADMINISTRADOR
// =========================================================

document.addEventListener("DOMContentLoaded", () => {

  // =======================================================
  // 1. ELEMENTOS DEL CHATBOT
  // =======================================================

  const chatFloatingButton =
    document.getElementById("chatFloatingButton");

  const openChatMenu =
    document.getElementById("openChatMenu");

  const chatPanel =
    document.getElementById("chatPanel");

  const chatOverlay =
    document.getElementById("chatOverlay");

  const closeChatButton =
    document.getElementById("closeChatButton");

  const expandChatButton =
    document.getElementById("expandChatButton");

  const newChatButton =
    document.getElementById("newChatButton");

  const chatInput =
    document.getElementById("chatInput");

  const chatSendButton =
    document.getElementById("chatSendButton");

  const chatMessages =
    document.getElementById("chatMessages");

  const chatWelcome =
    document.getElementById("chatWelcome");

  const chatGreeting =
    document.getElementById("chatGreeting");

  const chatRoleLabel =
    document.getElementById("chatRoleLabel");

  const chatSuggestions =
    document.getElementById("chatSuggestions");

  const chatPermissionText =
    document.getElementById("chatPermissionText");


  // =======================================================
  // 2. USUARIO ACTUAL
  // =======================================================
  // La sesión se guarda al iniciar sesión con Supabase/FastAPI.

  const storedProfile = (() => {
    try {
      return JSON.parse(localStorage.getItem("asistencia_profile") || "{}");
    } catch (_) {
      return {};
    }
  })();

  const currentUser = {
    id: storedProfile.id || null,
    nombre: storedProfile.nombres || "Usuario",
    nombreCompleto: `${storedProfile.nombres || ""} ${storedProfile.apellidos || ""}`.trim(),
    rol: storedProfile.rol || "ESTUDIANTE"
  };


  // =======================================================
  // 3. CONFIGURACIÓN SEGÚN ROL
  // =======================================================

  const roleConfig = {

    ESTUDIANTE: {

      label: "Estudiante",

      permission:
        "Solo puedes consultar información asociada a tu cuenta.",

      suggestions: [
        {
          icon: "fa-solid fa-chart-pie",
          text: "¿Cuál es mi porcentaje de asistencia?"
        },
        {
          icon: "fa-solid fa-user-xmark",
          text: "¿Cuántas faltas tengo?"
        },
        {
          icon: "fa-solid fa-clock",
          text: "¿Cuántas tardanzas tengo?"
        },
        {
          icon: "fa-solid fa-book-open",
          text: "Muéstrame mis cursos"
        },
        {
          icon: "fa-solid fa-calendar-days",
          text: "¿Cuál es mi próxima clase?"
        }
      ]
    },


    PROFESOR: {

      label: "Profesor",

      permission:
        "Puedes consultar información de tus cursos y de los estudiantes matriculados en ellos.",

      suggestions: [
        {
          icon: "fa-solid fa-user-check",
          text: "¿Quién faltó hoy?"
        },
        {
          icon: "fa-solid fa-chart-line",
          text: "¿Qué estudiantes tienen baja asistencia?"
        },
        {
          icon: "fa-solid fa-users",
          text: "Muéstrame la asistencia de mi curso"
        },
        {
          icon: "fa-solid fa-file-excel",
          text: "Genera un reporte de asistencia"
        },
        {
          icon: "fa-solid fa-clock",
          text: "¿Quiénes tienen más tardanzas?"
        }
      ]
    },


    ADMINISTRADOR: {

      label: "Administrador",

      permission:
        "Puedes consultar información general autorizada del sistema.",

      suggestions: [
        {
          icon: "fa-solid fa-chart-column",
          text: "Muéstrame la asistencia general"
        },
        {
          icon: "fa-solid fa-user-xmark",
          text: "¿Cuántos estudiantes faltaron hoy?"
        },
        {
          icon: "fa-solid fa-book-open",
          text: "¿Qué curso tiene más ausencias?"
        },
        {
          icon: "fa-solid fa-file-excel",
          text: "Genera un reporte general"
        },
        {
          icon: "fa-solid fa-brain",
          text: "Muéstrame las métricas del modelo"
        }
      ]
    }

  };


  // =======================================================
  // 4. OBTENER CONFIGURACIÓN DEL ROL
  // =======================================================

  function getCurrentRoleConfig() {

    return (
      roleConfig[currentUser.rol] ||
      roleConfig.ESTUDIANTE
    );

  }


  // =======================================================
  // 5. CONFIGURAR INTERFAZ
  // =======================================================

  function configureChatForUser() {

    const config =
      getCurrentRoleConfig();


    if (chatGreeting) {

      chatGreeting.textContent =
        `Hola, ${currentUser.nombre}`;

    }


    if (chatRoleLabel) {

      chatRoleLabel.textContent =
        config.label;

    }


    if (chatPermissionText) {

      chatPermissionText.textContent =
        config.permission;

    }


    renderSuggestions(
      config.suggestions
    );

  }


  // =======================================================
  // 6. RENDERIZAR SUGERENCIAS
  // =======================================================

  function renderSuggestions(suggestions) {

    if (!chatSuggestions) {
      return;
    }


    chatSuggestions.innerHTML = "";


    suggestions.forEach((suggestion) => {

      const button =
        document.createElement("button");


      button.type = "button";

      button.className =
        "chat-suggestion";


      button.dataset.message =
        suggestion.text;


      button.innerHTML = `
        <i class="${suggestion.icon}"></i>
        <span>${suggestion.text}</span>
      `;


      button.addEventListener(
        "click",
        () => {

          sendMessage(
            suggestion.text
          );

        }
      );


      chatSuggestions.appendChild(
        button
      );

    });

  }


  // =======================================================
  // 7. ABRIR CHAT
  // =======================================================

  function openChat() {

    if (!chatPanel) {
      return;
    }


    chatPanel.classList.add(
      "active"
    );


    if (chatOverlay) {

      chatOverlay.classList.add(
        "active"
      );

    }


    if (chatFloatingButton) {

      chatFloatingButton.style.display =
        "none";

    }


    setTimeout(() => {

      chatInput?.focus();

    }, 250);

  }


  // =======================================================
  // 8. CERRAR CHAT
  // =======================================================

  function closeChat() {

    if (!chatPanel) {
      return;
    }


    chatPanel.classList.remove(
      "active"
    );


    chatPanel.classList.remove(
      "fullscreen"
    );


    if (chatOverlay) {

      chatOverlay.classList.remove(
        "active"
      );

    }


    if (chatFloatingButton) {

      chatFloatingButton.style.display =
        "flex";

    }


    updateExpandIcon();

  }


  // =======================================================
  // 9. EVENTOS PARA ABRIR
  // =======================================================

  if (chatFloatingButton) {

    chatFloatingButton.addEventListener(
      "click",
      openChat
    );

  }


  if (openChatMenu) {

    openChatMenu.addEventListener(
      "click",
      (event) => {

        event.preventDefault();

        openChat();

      }
    );

  }


  // =======================================================
  // 10. EVENTOS PARA CERRAR
  // =======================================================

  if (closeChatButton) {

    closeChatButton.addEventListener(
      "click",
      closeChat
    );

  }


  if (chatOverlay) {

    chatOverlay.addEventListener(
      "click",
      closeChat
    );

  }


  // =======================================================
  // 11. AMPLIAR / REDUCIR CHAT
  // =======================================================

  function updateExpandIcon() {

    if (!expandChatButton) {
      return;
    }


    const icon =
      expandChatButton.querySelector("i");


    if (!icon) {
      return;
    }


    const isFullscreen =
      chatPanel?.classList.contains(
        "fullscreen"
      );


    if (isFullscreen) {

      icon.className =
        "fa-solid fa-compress";

      expandChatButton.title =
        "Reducir";

      expandChatButton.setAttribute(
        "aria-label",
        "Reducir chat"
      );

    } else {

      icon.className =
        "fa-solid fa-expand";

      expandChatButton.title =
        "Ampliar";

      expandChatButton.setAttribute(
        "aria-label",
        "Ampliar chat"
      );

    }

  }


  if (expandChatButton) {

    expandChatButton.addEventListener(
      "click",
      () => {

        if (!chatPanel) {
          return;
        }


        chatPanel.classList.toggle(
          "fullscreen"
        );


        updateExpandIcon();

      }
    );

  }


  // =======================================================
  // 12. NUEVA CONVERSACIÓN
  // =======================================================

  function newConversation() {

    if (chatMessages) {

      chatMessages.innerHTML = "";

    }


    if (chatWelcome) {

      chatWelcome.style.display =
        "block";

    }


    if (chatInput) {

      chatInput.value = "";

      resetTextareaHeight();

    }


    chatInput?.focus();

  }


  if (newChatButton) {

    newChatButton.addEventListener(
      "click",
      newConversation
    );

  }


  // =======================================================
  // 13. CREAR MENSAJE DEL USUARIO
  // =======================================================

  function createUserMessage(message) {

    const element =
      document.createElement("div");


    element.className =
      "chat-message-user";


    element.textContent =
      message;


    return element;

  }


  // =======================================================
  // 14. CREAR RESPUESTA DEL BOT
  // =======================================================

  function createBotMessage(message) {

    const container =
      document.createElement("div");


    container.className =
      "chat-message-bot";


    const icon =
      document.createElement("div");


    icon.className =
      "chat-message-bot-icon";


    icon.innerHTML = `
      <img
        src="../assets/img/chatbot/asistente-ia.png"
        alt="Asistente IA"
      >
    `;


    const content =
      document.createElement("div");


    content.className =
      "chat-message-bot-content";


    content.textContent =
      message;


    container.appendChild(
      icon
    );


    container.appendChild(
      content
    );


    return container;

  }


  // =======================================================
  // 15. INDICADOR ESCRIBIENDO
  // =======================================================

  function createTypingIndicator() {

    const container =
      document.createElement("div");


    container.className =
      "chat-message-bot";


    container.id =
      "chatTypingIndicator";


    const icon =
      document.createElement("div");


    icon.className =
      "chat-message-bot-icon";


    icon.innerHTML = `
      <img
        src="../assets/img/chatbot/asistente-ia.png"
        alt="Asistente IA"
      >
    `;


    const typing =
      document.createElement("div");


    typing.className =
      "chat-typing";


    typing.innerHTML = `
      <span></span>
      <span></span>
      <span></span>
    `;


    container.appendChild(
      icon
    );


    container.appendChild(
      typing
    );


    return container;

  }


  // =======================================================
  // 16. SCROLL AL ÚLTIMO MENSAJE
  // =======================================================

  function scrollToBottom() {

    const chatBody =
      document.getElementById(
        "chatBody"
      );


    if (!chatBody) {
      return;
    }


    requestAnimationFrame(() => {

      chatBody.scrollTop =
        chatBody.scrollHeight;

    });

  }


  // =======================================================
  // 17. LLAMAR AL BACKEND FASTAPI
  // =======================================================

  async function askBackend(message) {

    if (typeof apiRequest === "function") {
      const data = await apiRequest("/api/chatbot/message", {
        method: "POST",
        body: JSON.stringify({ message })
      });
      return data.response;
    }

    const token = localStorage.getItem("asistencia_access_token");
    const response = await fetch(
      "http://127.0.0.1:8000/api/chatbot/message",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ message })
      }
    );

    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}`);
    }

    const data = await response.json();
    return data.response;
  }


  // =======================================================
  // 18. ENVIAR MENSAJE
  // =======================================================

  async function sendMessage(messageText = null) {

    if (!chatInput || !chatMessages) {
      return;
    }


    const message =
      messageText !== null
        ? messageText.trim()
        : chatInput.value.trim();


    if (message === "") {
      return;
    }


    // Ocultar bienvenida
    if (chatWelcome) {

      chatWelcome.style.display =
        "none";

    }


    // Crear mensaje del usuario
    const userMessage =
      createUserMessage(
        message
      );


    chatMessages.appendChild(
      userMessage
    );


    // Limpiar input
    chatInput.value = "";

    resetTextareaHeight();

    scrollToBottom();


    // Deshabilitar botón mientras responde
    if (chatSendButton) {

      chatSendButton.disabled = true;

    }


    // Mostrar indicador escribiendo
    const typingIndicator =
      createTypingIndicator();


    chatMessages.appendChild(
      typingIndicator
    );


    scrollToBottom();


    let responseText;


    try {

      responseText =
        await askBackend(
          message
        );

    } catch (error) {

      console.error(
        "Error al conectar con FastAPI:",
        error
      );


      responseText =
        "No pude conectarme con el servidor. " +
        "Verifica que FastAPI esté ejecutándose en http://127.0.0.1:8000.";

    } finally {

      typingIndicator.remove();


      if (chatSendButton) {

        chatSendButton.disabled = false;

      }

    }


    const botMessage =
      createBotMessage(
        responseText
      );


    chatMessages.appendChild(
      botMessage
    );


    scrollToBottom();


    chatInput?.focus();

  }


  // =======================================================
  // 19. BOTÓN ENVIAR
  // =======================================================

  if (chatSendButton) {

    chatSendButton.addEventListener(
      "click",
      () => {

        sendMessage();

      }
    );

  }


  // =======================================================
  // 20. ENTER PARA ENVIAR
  // =======================================================

  if (chatInput) {

    chatInput.addEventListener(
      "keydown",
      (event) => {

        /*
          ENTER
          → enviar

          SHIFT + ENTER
          → nueva línea
        */

        if (
          event.key === "Enter" &&
          !event.shiftKey
        ) {

          event.preventDefault();

          sendMessage();

        }

      }
    );

  }


  // =======================================================
  // 21. TEXTAREA AUTOMÁTICO
  // =======================================================

  function resetTextareaHeight() {

    if (!chatInput) {
      return;
    }


    chatInput.style.height =
      "auto";

  }


  function resizeTextarea() {

    if (!chatInput) {
      return;
    }


    chatInput.style.height =
      "auto";


    const maxHeight =
      110;


    chatInput.style.height =
      Math.min(
        chatInput.scrollHeight,
        maxHeight
      ) + "px";

  }


  if (chatInput) {

    chatInput.addEventListener(
      "input",
      resizeTextarea
    );

  }


  // =======================================================
  // 22. ESC PARA CERRAR
  // =======================================================

  document.addEventListener(
    "keydown",
    (event) => {

      if (
        event.key === "Escape" &&
        chatPanel?.classList.contains(
          "active"
        )
      ) {

        closeChat();

      }

    }
  );


  // =======================================================
  // 23. ASISTENTE DE VOZ (STT y TTS)
  // =======================================================

  const chatMicButton = document.getElementById("chatMicButton");

  let recognition = null;
  let isListening = false;

  if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = "es-ES";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      isListening = true;
      if (chatMicButton) {
        chatMicButton.classList.add("listening");
      }
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (chatInput) {
        chatInput.value = transcript;
        sendMessage();
      }
    };

    recognition.onerror = (event) => {
      console.error("Error en reconocimiento de voz:", event.error);
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
    };
  }

  function stopListening() {
    isListening = false;
    if (chatMicButton) {
      chatMicButton.classList.remove("listening");
    }
  }

  if (chatMicButton) {
    chatMicButton.addEventListener("click", () => {
      if (!recognition) {
        alert("El reconocimiento de voz no está soportado en este navegador.");
        return;
      }
      if (isListening) {
        recognition.stop();
      } else {
        recognition.start();
      }
    });
  }

  function speakResponse(text) {
    if (!("speechSynthesis" in window)) return;
    
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "es-ES";
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    // Quitar emojis y markdown para la voz
    utterance.text = text.replace(/[\u{1F600}-\u{1F6FF}\u{1F300}-\u{1F5FF}\u{1F900}-\u{1F9FF}]/gu, '')
                         .replace(/\*+/g, '')
                         .replace(/#+/g, '');

    window.speechSynthesis.speak(utterance);
  }

  // Modificar createBotMessage para que hable si el panel está abierto
  const originalCreateBotMessage = createBotMessage;
  createBotMessage = function(message) {
    speakResponse(message);
    return originalCreateBotMessage(message);
  };

  // =======================================================
  // 24. INICIALIZACIÓN
  // =======================================================

  configureChatForUser();

  updateExpandIcon();

});