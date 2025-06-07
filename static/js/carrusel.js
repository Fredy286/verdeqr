// Carrusel de sugerencias
document.addEventListener('DOMContentLoaded', function() {
    // Obtener todas las sugerencias y guardarlas en un array
    const carrusel = document.querySelector('.carrusel-sugerencias');
    if (!carrusel) return; // Si no hay carrusel, salir
    
    const sugerencias = Array.from(document.querySelectorAll('.sugerencia-card'));
    const totalSugerencias = sugerencias.length;
    
    console.log(`Total sugerencias encontradas: ${totalSugerencias}`);
    
    // Si no hay sugerencias, salir
    if (totalSugerencias === 0) return;
    
    // Determinar cuántas tarjetas mostrar por página según el ancho de la pantalla
    let cardsPerPage = 1;
    if (window.innerWidth >= 1200) {
        cardsPerPage = 5;
    } else if (window.innerWidth >= 768) {
        cardsPerPage = 3;
    }
    
    // Guardar una copia de todas las sugerencias originales
    const todasLasSugerencias = [];
    sugerencias.forEach(card => {
        // Clonar cada tarjeta y guardarla
        const clone = card.cloneNode(true);
        todasLasSugerencias.push(clone);
        // Ocultar la tarjeta original
        card.style.display = 'none';
    });
    
    // Calcular el número total de páginas
    const totalPages = Math.max(1, Math.ceil(totalSugerencias / cardsPerPage));
    let currentPage = 0;
    let autoChangeInterval;
    
    console.log(`Total páginas: ${totalPages}, Cards per page: ${cardsPerPage}`);
    
    function mostrarSugerencias(page) {
        // Limpiar el carrusel
        carrusel.innerHTML = '';
        
        // Calcular índices de inicio y fin para esta página
        const start = page * cardsPerPage;
        const end = Math.min(start + cardsPerPage, totalSugerencias);
        
        console.log(`Mostrando sugerencias de ${start} a ${end-1}`);
        
        // Crear un contenedor para las sugerencias activas
        const activeContainer = document.createElement('div');
        activeContainer.style.display = 'flex';
        activeContainer.style.gap = '20px';
        activeContainer.style.width = '100%';
        activeContainer.style.justifyContent = 'center';
        activeContainer.style.flexWrap = 'wrap';
        
        // Mostrar las sugerencias de la página actual
        for (let i = start; i < end; i++) {
            if (i < totalSugerencias) {
                // Clonar la tarjeta original para evitar problemas con el DOM
                const card = todasLasSugerencias[i].cloneNode(true);
                card.style.display = 'block';
                card.style.opacity = '1';
                card.style.transform = 'translateX(0)';
                card.style.flex = '0 0 calc(20% - 20px)';
                card.style.minWidth = '200px';
                card.style.maxWidth = '300px';
                card.style.backgroundColor = 'white';
                card.style.borderRadius = '10px';
                card.style.padding = '1.5rem';
                card.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                card.style.margin = '10px';
                activeContainer.appendChild(card);
            }
        }
        
        // Agregar el contenedor al carrusel
        carrusel.appendChild(activeContainer);
    }
    
    // Función para cambiar las sugerencias
    window.cambiarSugerencias = function(direction) {
        // Calcular la nueva página
        let newPage = currentPage + direction;
        
        // Manejar el ciclo de páginas
        if (newPage >= totalPages) {
            newPage = 0;
        } else if (newPage < 0) {
            newPage = totalPages - 1;
        }
        
        console.log(`Cambiando de página ${currentPage} a ${newPage}`);
        currentPage = newPage;
        
        // Mostrar las sugerencias de la nueva página
        mostrarSugerencias(currentPage);
        
        // Reiniciar el intervalo automático
        clearInterval(autoChangeInterval);
        autoChangeInterval = setInterval(() => cambiarSugerencias(1), 5000);
    };
    
    // Iniciar el cambio automático
    autoChangeInterval = setInterval(() => cambiarSugerencias(1), 5000);
    
    // Mostrar la primera página al cargar
    mostrarSugerencias(0);
    
    // Actualizar el número de tarjetas por página cuando cambia el tamaño de la ventana
    window.addEventListener('resize', function() {
        let newCardsPerPage = 1;
        if (window.innerWidth >= 1200) {
            newCardsPerPage = 5;
        } else if (window.innerWidth >= 768) {
            newCardsPerPage = 3;
        }
        
        if (newCardsPerPage !== cardsPerPage) {
            // Recalcular y mostrar
            cardsPerPage = newCardsPerPage;
            const newTotalPages = Math.max(1, Math.ceil(totalSugerencias / cardsPerPage));
            totalPages = newTotalPages;
            currentPage = Math.min(currentPage, totalPages - 1);
            mostrarSugerencias(currentPage);
        }
    });
});
