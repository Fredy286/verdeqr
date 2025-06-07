// Script para el carrusel de sugerencias con animación mejorada
document.addEventListener('DOMContentLoaded', function() {
    // Variables para el carrusel
    const carrusel = document.querySelector('.carrusel-sugerencias');
    if (!carrusel) return;
    
    // Obtener todas las tarjetas de sugerencias
    let sugerencias = Array.from(document.querySelectorAll('.sugerencia-card'));
    const totalSugerencias = sugerencias.length;
    
    // Si no hay sugerencias, salir
    if (totalSugerencias === 0) return;
    
    // Asegurarse de que todas las tarjetas sean visibles inicialmente
    sugerencias.forEach(card => {
        card.style.opacity = '1';
        card.style.transform = 'none';
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
    let isAnimating = false;
    
    // Crear indicadores de página
    const carouselContainer = document.querySelector('.carrusel-container');
    const paginationContainer = document.createElement('div');
    paginationContainer.className = 'carousel-pagination';
    
    for (let i = 0; i < totalPages; i++) {
        const indicator = document.createElement('span');
        indicator.className = 'carousel-indicator';
        if (i === 0) indicator.classList.add('active');
        indicator.setAttribute('data-page', i);
        indicator.addEventListener('click', function() {
            if (!isAnimating) {
                const targetPage = parseInt(this.getAttribute('data-page'));
                if (targetPage !== currentPage) {
                    cambiarSugerencias(targetPage - currentPage);
                }
            }
        });
        paginationContainer.appendChild(indicator);
    }
    
    if (carouselContainer) {
        carouselContainer.appendChild(paginationContainer);
    }
    
    // Función para actualizar los indicadores de página
    function updatePagination() {
        const indicators = document.querySelectorAll('.carousel-indicator');
        indicators.forEach((indicator, index) => {
            if (index === currentPage) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });
    }
    
    // Función para cambiar a la siguiente/anterior página
    window.cambiarSugerencias = function(direction) {
        if (isAnimating) return;
        isAnimating = true;
        
        // Calcular la nueva página
        let newPage;
        if (typeof direction === 'number' && Math.abs(direction) > 1) {
            // Si se proporciona un número de página específico
            newPage = direction;
        } else {
            // Si se proporciona una dirección (1 o -1)
            newPage = currentPage + direction;
            
            // Manejar los límites de páginas
            if (newPage >= totalPages) {
                newPage = 0; // Volver al inicio
            } else if (newPage < 0) {
                newPage = totalPages - 1; // Ir al final
            }
        }
        
        // Asegurarse de que la nueva página sea válida
        if (newPage >= totalPages) newPage = totalPages - 1;
        if (newPage < 0) newPage = 0;
        
        // Si no hay cambio, no hacer nada
        if (newPage === currentPage) {
            isAnimating = false;
            return;
        }
        
        // Calcular índices para la página actual y la nueva
        const currentStart = currentPage * cardsPerPage;
        const currentEnd = Math.min(currentStart + cardsPerPage, totalSugerencias);
        const newStart = newPage * cardsPerPage;
        const newEnd = Math.min(newStart + cardsPerPage, totalSugerencias);
        
        // Determinar la dirección de la animación
        const animationDirection = newPage > currentPage ? 1 : -1;
        
        // Animar la salida de las tarjetas actuales
        for (let i = currentStart; i < currentEnd; i++) {
            if (i < totalSugerencias) {
                const card = sugerencias[i];
                card.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                card.style.opacity = '0';
                card.style.transform = animationDirection > 0 ? 'translateX(-50px)' : 'translateX(50px)';
            }
        }
        
        // Después de un breve retraso, animar la entrada de las nuevas tarjetas
        setTimeout(() => {
            // Ocultar todas las tarjetas primero
            sugerencias.forEach(card => {
                card.style.display = 'none';
            });
            
            // Mostrar y animar las nuevas tarjetas
            for (let i = newStart; i < newEnd; i++) {
                if (i < totalSugerencias) {
                    const card = sugerencias[i];
                    const delay = (i - newStart) * 0.1;
                    
                    // Preparar la tarjeta para la animación
                    card.style.display = 'block';
                    card.style.opacity = '0';
                    card.style.transform = animationDirection > 0 ? 'translateX(50px)' : 'translateX(-50px)';
                    
                    // Animar la entrada con un retraso escalonado
                    setTimeout(() => {
                        card.style.transition = 'all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                        card.style.opacity = '1';
                        card.style.transform = 'translateX(0)';
                    }, delay * 1000);
                }
            }
            
            // Actualizar la página actual
            currentPage = newPage;
            updatePagination();
            
            // Permitir nuevas animaciones después de que termine esta
            setTimeout(() => {
                isAnimating = false;
            }, 500);
        }, 500);
        
        // Reiniciar el intervalo automático
        clearInterval(autoChangeInterval);
        autoChangeInterval = setInterval(() => {
            cambiarSugerencias(1);
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
                // Recrear los indicadores de página
                paginationContainer.innerHTML = '';
                for (let i = 0; i < totalPages; i++) {
                    const indicator = document.createElement('span');
                    indicator.className = 'carousel-indicator';
                    if (i === currentPage) indicator.classList.add('active');
                    indicator.setAttribute('data-page', i);
                    indicator.addEventListener('click', function() {
                        if (!isAnimating) {
                            const targetPage = parseInt(this.getAttribute('data-page'));
                            if (targetPage !== currentPage) {
                                cambiarSugerencias(targetPage - currentPage);
                            }
                        }
                    });
                    paginationContainer.appendChild(indicator);
                }
                
                // Mostrar las tarjetas de la página actual
                sugerencias.forEach((card, index) => {
                    const isInCurrentPage = index >= currentPage * cardsPerPage && index < (currentPage + 1) * cardsPerPage;
                    card.style.display = isInCurrentPage ? 'block' : 'none';
                    if (isInCurrentPage) {
                        card.style.opacity = '1';
                        card.style.transform = 'translateX(0)';
                    }
                });
            }
        }
    });
    
    // Añadir estilos para los nuevos elementos
    const style = document.createElement('style');
    style.textContent = `
        .carousel-pagination {
            display: flex;
            justify-content: center;
            margin-top: 20px;
            gap: 8px;
        }
        
        .carousel-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: rgba(52, 152, 219, 0.3);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .carousel-indicator.active {
            background-color: #3498db;
            transform: scale(1.2);
        }
        
        .carousel-indicator:hover {
            background-color: rgba(52, 152, 219, 0.7);
        }
        
        .sugerencia-card {
            opacity: 1 !important;
            transform: none !important;
        }
    `;
    
    document.head.appendChild(style);
    
    // Mostrar solo las tarjetas de la primera página inicialmente
    sugerencias.forEach((card, index) => {
        const isInFirstPage = index < cardsPerPage;
        card.style.display = isInFirstPage ? 'block' : 'none';
        if (isInFirstPage) {
            card.style.opacity = '1';
            card.style.transform = 'translateX(0)';
        }
    });
    
    // Iniciar el cambio automático
    autoChangeInterval = setInterval(() => {
        cambiarSugerencias(1);
    }, 5000);
});
