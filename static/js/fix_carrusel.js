// Script para el carrusel de sugerencias - Versión mejorada para responsive
document.addEventListener('DOMContentLoaded', function() {
    // Variables para el carrusel
    const carrusel = document.querySelector('.carrusel-sugerencias');
    if (!carrusel) return;

    // Obtener todas las tarjetas de sugerencias
    let sugerencias = Array.from(document.querySelectorAll('.sugerencia-card'));
    const totalSugerencias = sugerencias.length;

    // Si no hay sugerencias, salir
    if (totalSugerencias === 0) return;

    // Guardar una copia de todas las sugerencias originales
    const sugerenciasOriginales = [];
    sugerencias.forEach(card => {
        const clone = card.cloneNode(true);
        sugerenciasOriginales.push(clone);
    });

    // Determinar cuántas tarjetas mostrar por página según el ancho de la pantalla
    function getCardsPerPage() {
        if (window.innerWidth >= 1400) return 5;
        if (window.innerWidth >= 1200) return 4;
        if (window.innerWidth >= 992) return 3;
        if (window.innerWidth >= 768) return 2;
        return 1;
    }

    let cardsPerPage = getCardsPerPage();
    let currentPage = 0;
    let totalPages = Math.ceil(totalSugerencias / cardsPerPage);
    let autoChangeInterval;

    // Función para mostrar las sugerencias de una página específica
    function mostrarSugerencias(page) {
        // Limpiar el carrusel
        while (carrusel.firstChild) {
            carrusel.removeChild(carrusel.firstChild);
        }

        // Calcular índices de inicio y fin para esta página
        const start = page * cardsPerPage;
        const end = Math.min(start + cardsPerPage, totalSugerencias);

        // Mostrar las sugerencias de la página actual
        for (let i = start; i < end; i++) {
            if (i < totalSugerencias) {
                // Clonar la tarjeta original para evitar problemas con el DOM
                const card = sugerenciasOriginales[i].cloneNode(true);

                // Aplicar estilos y animaciones
                const delay = (i - start) * 0.1;
                card.setAttribute('data-delay', delay);
                card.style.animation = `fadeIn 0.5s ease forwards ${delay}s`;

                // Agregar la tarjeta al carrusel
                carrusel.appendChild(card);
            }
        }

        // Actualizar visibilidad de botones
        updateButtonsVisibility();
    }

    // Función para actualizar la visibilidad de los botones
    function updateButtonsVisibility() {
        const prevBtn = document.querySelector('.carrusel-btn.prev');
        const nextBtn = document.querySelector('.carrusel-btn.next');

        if (prevBtn) {
            prevBtn.style.opacity = currentPage === 0 ? '0.5' : '1';
            prevBtn.style.pointerEvents = currentPage === 0 ? 'none' : 'auto';
        }

        if (nextBtn) {
            const isAtEnd = currentPage >= totalPages - 1;
            nextBtn.style.opacity = isAtEnd ? '0.5' : '1';
            nextBtn.style.pointerEvents = isAtEnd ? 'none' : 'auto';
        }
    }

    // Función para cambiar a la siguiente/anterior página
    window.cambiarSugerencias = function(direction) {
        // Calcular la nueva página
        let newPage = currentPage + direction;

        // Manejar los límites de páginas
        if (newPage >= totalPages) {
            newPage = totalPages - 1;
        } else if (newPage < 0) {
            newPage = 0;
        }

        // Si no hay cambio, no hacer nada
        if (newPage === currentPage) return;

        currentPage = newPage;

        // Mostrar las sugerencias de la nueva página
        mostrarSugerencias(currentPage);

        // Reiniciar el intervalo automático
        clearInterval(autoChangeInterval);
        autoChangeInterval = setInterval(() => {
            // Solo avanzar si no estamos en la última página
            if (currentPage < totalPages - 1) {
                cambiarSugerencias(1);
            } else {
                // Volver al inicio si estamos en la última página
                currentPage = -1; // Se incrementará a 0 en cambiarSugerencias
                cambiarSugerencias(1);
            }
        }, 5000);
    };

    // Actualizar la configuración cuando cambia el tamaño de la ventana
    window.addEventListener('resize', function() {
        const newCardsPerPage = getCardsPerPage();

        if (newCardsPerPage !== cardsPerPage) {
            cardsPerPage = newCardsPerPage;
            const oldTotalPages = totalPages;
            totalPages = Math.ceil(totalSugerencias / cardsPerPage);

            // Ajustar la página actual si es necesario
            if (currentPage >= totalPages) {
                currentPage = totalPages - 1;
            }

            // Actualizar el carrusel solo si cambió el número de páginas
            if (oldTotalPages !== totalPages) {
                mostrarSugerencias(currentPage);
            }
        }
    });

    // Iniciar el carrusel
    mostrarSugerencias(0);

    // Iniciar el cambio automático
    autoChangeInterval = setInterval(() => {
        if (currentPage < totalPages - 1) {
            cambiarSugerencias(1);
        } else {
            currentPage = -1;
            cambiarSugerencias(1);
        }
    }, 5000);
});
