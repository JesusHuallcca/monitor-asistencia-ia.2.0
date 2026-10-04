// ==========================================
// DASHBOARD ESTUDIANTE - ASISTENCIA IA
// ==========================================

document.addEventListener("DOMContentLoaded", () => {


  // ========================================
  // 1. ELEMENTOS DE CURSOS
  // ========================================

  const courseSearch =
    document.getElementById("courseSearch");

  const statusFilter =
    document.getElementById("statusFilter");

  const periodFilter =
    document.getElementById("periodFilter");

  const courseCards =
    document.querySelectorAll(".course-card");

  const courseCount =
    document.querySelector(".course-count");



  // ========================================
  // 2. FUNCIÓN GENERAL DE FILTRADO
  // ========================================

  function filterCourses() {

    const searchValue = courseSearch
      ? courseSearch.value.toLowerCase().trim()
      : "";

    const selectedStatus = statusFilter
      ? statusFilter.value
      : "todos";

    let visibleCourses = 0;


    courseCards.forEach((card) => {

      // NOMBRE DEL CURSO
      const courseName =
        card.dataset.name
          ? card.dataset.name.toLowerCase()
          : "";


      // ESTADO DEL CURSO
      const statusElement =
        card.querySelector(".status");

      const courseStatus =
        statusElement
          ? statusElement.textContent.toLowerCase().trim()
          : "";


      // ----------------------------------------
      // Coincidencia por búsqueda
      // ----------------------------------------

      const matchesSearch =
        courseName.includes(searchValue);


      // ----------------------------------------
      // Coincidencia por estado
      // ----------------------------------------

      let matchesStatus = true;


      if (selectedStatus === "activo") {

        matchesStatus =
          courseStatus === "en curso";

      }


      if (selectedStatus === "finalizado") {

        matchesStatus =
          courseStatus === "finalizado";

      }


      if (selectedStatus === "todos") {

        matchesStatus = true;

      }


      // ----------------------------------------
      // Mostrar / ocultar
      // ----------------------------------------

      const shouldShow =
        matchesSearch &&
        matchesStatus;


      if (shouldShow) {

        card.style.display = "";
        visibleCourses++;

      } else {

        card.style.display = "none";

      }

    });



    // ========================================
    // ACTUALIZAR CONTADOR
    // ========================================

    if (courseCount) {

      if (visibleCourses === 1) {

        courseCount.textContent =
          "1 curso encontrado";

      } else {

        courseCount.textContent =
          `${visibleCourses} cursos encontrados`;

      }

    }

  }



  // ========================================
  // 3. BUSCADOR DE CURSOS
  // ========================================

  if (courseSearch) {

    courseSearch.addEventListener(
      "input",
      filterCourses
    );

  }



  // ========================================
  // 4. FILTRO POR ESTADO
  // ========================================

  if (statusFilter) {

    statusFilter.addEventListener(
      "change",
      filterCourses
    );

  }



  // ========================================
  // 5. FILTRO POR PERÍODO
  // ========================================

  if (periodFilter) {

    periodFilter.addEventListener(
      "change",
      () => {

        const selectedPeriod =
          periodFilter.value;

        console.log(
          "Período seleccionado:",
          selectedPeriod
        );


        /*
          MÁS ADELANTE:

          Cuando tengamos FastAPI conectado,
          aquí podremos consultar:

          GET /api/courses?period=2026-2

          Por ahora los cursos son datos
          de demostración.
        */

      }
    );

  }



  // ========================================
  // 6. MENÚ LATERAL RESPONSIVE
  // ========================================

  const menuButton =
    document.getElementById("menuButton");

  const sidebar =
    document.querySelector(".sidebar");


  if (menuButton && sidebar) {

    menuButton.addEventListener(
      "click",
      () => {

        sidebar.classList.toggle("open");

      }
    );

  }



  // ========================================
  // 7. CERRAR SIDEBAR EN MÓVIL
  // ========================================

  document.addEventListener(
    "click",
    (event) => {

      if (!sidebar || !menuButton) {
        return;
      }


      if (window.innerWidth > 760) {
        return;
      }


      const clickedSidebar =
        sidebar.contains(event.target);

      const clickedMenuButton =
        menuButton.contains(event.target);


      if (
        !clickedSidebar &&
        !clickedMenuButton
      ) {

        sidebar.classList.remove("open");

      }

    }
  );



  // ========================================
  // 8. NAVEGACIÓN SPA POR SECCIONES
  // ========================================

  const menuItems = document.querySelectorAll(".menu-item");
  const spaSections = document.querySelectorAll(".spa-section");

  function navigateToSection(sectionId) {
    if (!sectionId) return;

    // Ocultar todas las secciones
    spaSections.forEach((sec) => {
      sec.style.display = "none";
      sec.classList.remove("active");
    });

    // Buscar sección objetivo
    let targetSection = document.querySelector(`.spa-section[data-section="${sectionId}"]`) ||
                        document.getElementById(`section-${sectionId}`);

    if (!targetSection && (sectionId === "inicio" || sectionId === "")) {
      targetSection = document.getElementById("section-inicio");
    }

    if (targetSection) {
      targetSection.style.display = "";
      targetSection.classList.add("active");
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    // Actualizar clase activa en sidebar
    menuItems.forEach((menuItem) => {
      if (menuItem.dataset.section === sectionId) {
        menuItem.classList.add("active");
      } else if (menuItem.dataset.section) {
        menuItem.classList.remove("active");
      }
    });

    // Cerrar sidebar en móvil tras navegar
    if (sidebar && window.innerWidth <= 760) {
      sidebar.classList.remove("open");
    }
  }

  menuItems.forEach((item) => {
    if (item.id === "openChatMenu" || item.id === "logoutLink") {
      return;
    }

    item.addEventListener("click", (e) => {
      const section = item.dataset.section;
      if (section) {
        e.preventDefault();
        navigateToSection(section);
        try {
          history.replaceState(null, "", `#${section}`);
        } catch (_) {}
      }
    });
  });

  // Cargar sección según hash inicial (ej: #calendario o #asistencia)
  const initialHash = window.location.hash.replace("#", "").trim();
  if (initialHash) {
    navigateToSection(initialHash);
  }



  // ========================================
  // 9. BUSCADOR GENERAL
  // ========================================

  const globalSearch =
    document.getElementById("globalSearch");


  if (globalSearch) {

    globalSearch.addEventListener(
      "keydown",
      (event) => {

        if (event.key !== "Enter") {
          return;
        }


        const value =
          globalSearch.value.trim();


        if (value === "") {
          return;
        }


        console.log(
          "Búsqueda general:",
          value
        );


        /*
          MÁS ADELANTE:

          Esta búsqueda podrá consultar:
          - cursos
          - contenidos
          - profesores
          - actividades

          mediante FastAPI.
        */

      }
    );

  }



  // ========================================
  // 10. BOTONES IR AL CURSO
  // ========================================

  const courseLinks =
    document.querySelectorAll(
      ".course-link"
    );


  courseLinks.forEach((link) => {

    link.addEventListener(
      "click",
      () => {

        const courseCard =
          link.closest(
            ".course-card"
          );


        const courseName =
          courseCard
            ?.querySelector("h3")
            ?.textContent
            ?.trim()
          || "Curso";


        console.log(
          `Ingresando al curso: ${courseName}`
        );

      }
    );

  });



  // ========================================
  // 11. BOTONES DE TRES PUNTOS DE CURSOS
  // ========================================

  const courseMenuButtons =
    document.querySelectorAll(
      ".course-heading button"
    );


  courseMenuButtons.forEach(
    (button) => {

      button.addEventListener(
        "click",
        (event) => {

          event.stopPropagation();


          const courseCard =
            button.closest(
              ".course-card"
            );


          const courseName =
            courseCard
              ?.querySelector("h3")
              ?.textContent
              ?.trim()
            || "Curso";


          console.log(
            `Opciones del curso: ${courseName}`
          );


          /*
            Después podremos mostrar:

            - Ver curso
            - Ver asistencia
            - Ver calendario
            - Ver profesor
          */

        }
      );

    }
  );



  // ========================================
  // 12. NOTIFICACIONES
  // ========================================

  const notificationButton =
    document.querySelector(
      ".notification"
    );


  if (notificationButton) {

    notificationButton.addEventListener(
      "click",
      () => {

        console.log(
          "Abrir notificaciones"
        );

      }
    );

  }



  // ========================================
  // 13. PERFIL DEL ESTUDIANTE
  // ========================================

  const profile =
    document.querySelector(".profile");


  if (profile) {

    profile.addEventListener(
      "click",
      () => {

        console.log(
          "Abrir menú de perfil"
        );

      }
    );

  }



  // ========================================
  // 14. INICIALIZAR FILTROS
  // ========================================

  filterCourses();


  // ========================================
  // 15. INTERACCIÓN DE MENSAJES (BANDEJA)
  // ========================================

  const messagesData = {
    "msg-1": {
      from: "Prof. Carlos Mendoza",
      time: "Hoy a las 10:30 AM",
      avatar: "../assets/img/usuarios/profesor.jpg",
      body: "Estimado estudiante,\n\nLe recuerdo que el examen parcial de Programación en Python se realizará el próximo viernes en el Laboratorio 301. Se evaluarán los temas de estructuras de datos avanzadas, funciones lambda y programación orientada a objetos.\n\nFavor de presentarse con 10 minutos de anticipación.\n\nAtentamente,\nProf. Carlos Mendoza"
    },
    "msg-2": {
      from: "Prof. Ana Torres",
      time: "Hoy a las 07:15 AM",
      avatar: "../assets/img/usuarios/profesor.jpg",
      body: "Hola a todos,\n\nLas diapositivas y el cuaderno Jupyter sobre Redes Neuronales convolucionales de la sesión anterior ya están subidos en el campus virtual. Les recomiendo revisarlo antes del laboratorio del jueves.\n\nSaludos cordiales,\nProf. Ana Torres"
    },
    "msg-3": {
      from: "Grupo Python - Proyecto Final",
      time: "Ayer a las 18:40 PM",
      avatar: "../assets/img/usuarios/alumno.jpg",
      body: "¿Hola chicos! ¿A qué hora nos reunimos mañana para revisar el avance de la interfaz y la integración con la base de datos? Propongo juntarnos por Discord o en la biblioteca a las 4:00 PM."
    },
    "msg-4": {
      from: "Prof. Luis Ramírez",
      time: "Hace 2 días",
      avatar: "../assets/img/usuarios/profesor.jpg",
      body: "Estimados estudiantes,\n\nLas notas del Cuestionario 02 de Estadística ya se encuentran publicadas en la pestaña de Calificaciones. Si alguien tiene alguna consulta sobre su puntuación, pueden escribir por este medio o en horas de asesoría los miércoles.\n\nSaludos."
    }
  };

  const msgItems = document.querySelectorAll(".msg-item");
  const msgEmpty = document.getElementById("msgEmpty");
  const msgContent = document.getElementById("msgContent");
  const msgFrom = document.getElementById("msgFrom");
  const msgTime = document.getElementById("msgTime");
  const msgBody = document.getElementById("msgBody");
  const msgAvatar = document.getElementById("msgAvatar");

  msgItems.forEach((item) => {
    item.addEventListener("click", () => {
      msgItems.forEach((m) => m.classList.remove("active"));
      item.classList.add("active");

      // Remover badge de no leído
      const badge = item.querySelector(".msg-badge");
      if (badge) badge.style.display = "none";
      item.classList.remove("unread");

      const msgId = item.id;
      const data = messagesData[msgId];
      if (data && msgContent && msgEmpty) {
        msgEmpty.style.display = "none";
        msgContent.style.display = "flex";
        msgContent.style.flexDirection = "column";
        msgFrom.textContent = data.from;
        msgTime.textContent = data.time;
        msgBody.innerText = data.body;
        if (msgAvatar) msgAvatar.src = data.avatar;
      }
    });
  });


  // ========================================
  // 16. FILTRO DE ASISTENCIA
  // ========================================

  const attendanceCourseFilter = document.getElementById("attendanceCourseFilter");
  const attendanceRows = document.querySelectorAll("#attendanceTableBody tr");

  if (attendanceCourseFilter) {
    attendanceCourseFilter.addEventListener("change", () => {
      const filter = attendanceCourseFilter.value;
      attendanceRows.forEach((row) => {
        const rowCourse = row.dataset.course;
        if (filter === "todos" || rowCourse === filter) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  }


  // ========================================
  // 17. BOTÓN CONSULTAR ASISTENTE IA
  // ========================================

  const statsAskAiBtn = document.getElementById("statsAskAiBtn");
  if (statsAskAiBtn) {
    statsAskAiBtn.addEventListener("click", () => {
      const openChatBtn = document.getElementById("chatFloatingButton") || document.getElementById("openChatMenu");
      if (openChatBtn) {
        openChatBtn.click();
      }
      const chatInput = document.getElementById("chatInput");
      if (chatInput) {
        chatInput.value = "¿Cuál es mi estado actual de asistencia y en qué curso debo tener mayor cuidado?";
        chatInput.focus();
      }
    });
  }


  // ========================================
  // 18. CARGAR DATOS DE SESIÓN EN PERFIL
  // ========================================

  try {
    if (typeof AsistenciaAuth !== "undefined") {
      const currentUser = AsistenciaAuth.getCurrentUser();
      if (currentUser) {
        const emailEl = document.getElementById("profileEmail");
        if (emailEl) emailEl.textContent = currentUser.correo || currentUser.email || "estudiante@institucion.edu.pe";
      }
    }
  } catch (err) {
    console.warn("No se pudo cargar datos del perfil:", err);
  }

});