// Script para mejorar la animación del carrusel de sugerencias
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
    let isAnimating = false;
    
    // Crear contenedor para la animación
    const carouselContainer = document.querySelector('.carrusel-container');
    const animationContainer = document.createElement('div');
    animationContainer.className = 'carousel-animation-container';
    
    // Reemplazar el carrusel original con el contenedor de animación
    if (carouselContainer) {
        carouselContainer.insertBefore(animationContainer, carrusel);
        animationContainer.appendChild(carrusel);
    }
    
    // Crear indicadores de página
    const paginationContainer = document.createElement('div');
    paginationContainer.className = 'carousel-pagination';
    for (let i = 0; i < totalPages; i++) {
        const indicator = document.createElement('span');
        indicator.className = 'carousel-indicator';
        indicator.setAttribute('data-page', i);
        indicator.addEventListener('click', () => {
            if (!isAnimating && i !== currentPage) {
                cambiarSugerencias(i - currentPage);
            }
        });
        paginationContainer.appendChild(indicator);
    }
    if (carouselContainer) {
        carouselContainer.appendChild(paginationContainer);
    }
    
    // Actualizar indicadores de página
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
    
    // Función para mostrar las sugerencias con animación mejorada
    function mostrarSugerencias(page, direction) {
        if (isAnimating) return;
        isAnimating = true;
        
        // Crear un nuevo conjunto de tarjetas
        const nuevoCarrusel = document.createElement('div');
        nuevoCarrusel.className = 'carrusel-sugerencias nuevo';
        
        // Calcular índices de inicio y fin para esta página
        const start = page * cardsPerPage;
        const end = Math.min(start + cardsPerPage, totalSugerencias);
        
        // Agregar las nuevas tarjetas
        for (let i = start; i < end; i++) {
            if (i < totalSugerencias) {
                const card = sugerenciasOriginales[i].cloneNode(true);
                card.style.opacity = '0';
                card.style.transform = direction > 0 ? 'translateX(50px)' : 'translateX(-50px)';
                nuevoCarrusel.appendChild(card);
            }
        }
        
        // Agregar el nuevo carrusel al contenedor
        animationContainer.appendChild(nuevoCarrusel);
        
        // Animar la salida del carrusel actual
        carrusel.style.transition = 'all 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
        carrusel.style.transform = direction > 0 ? 'translateX(-100px)' : 'translateX(100px)';
        carrusel.style.opacity = '0';
        carrusel.style.filter = 'blur(5px)';
        
        // Después de un breve retraso, animar la entrada del nuevo carrusel
        setTimeout(() => {
            nuevoCarrusel.style.transition = 'all 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            nuevoCarrusel.style.opacity = '1';
            nuevoCarrusel.style.transform = 'translateX(0)';
            
            // Animar cada tarjeta individualmente
            const nuevasTarjetas = nuevoCarrusel.querySelectorAll('.sugerencia-card');
            nuevasTarjetas.forEach((card, index) => {
                setTimeout(() => {
                    card.style.transition = 'all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                    card.style.opacity = '1';
                    card.style.transform = 'translateX(0)';
                    
                    // Añadir efecto de brillo
                    setTimeout(() => {
                        const glowEffect = document.createElement('div');
                        glowEffect.className = 'card-glow-effect';
                        card.appendChild(glowEffect);
                        
                        setTimeout(() => {
                            if (glowEffect && glowEffect.parentNode === card) {
                                card.removeChild(glowEffect);
                            }
                        }, 1000);
                    }, index * 100);
                }, index * 100);
            });
        }, 300);
        
        // Eliminar el carrusel anterior después de la animación
        setTimeout(() => {
            if (carrusel.parentNode === animationContainer) {
                animationContainer.removeChild(carrusel);
            }
            
            // El nuevo carrusel se convierte en el actual
            nuevoCarrusel.classList.remove('nuevo');
            window.carrusel = nuevoCarrusel;
            carrusel = nuevoCarrusel;
            
            // Actualizar visibilidad de botones
            updateButtonsVisibility();
            updatePagination();
            
            isAnimating = false;
        }, 1000);
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
        if (isAnimating) return;
        
        // Si es un número específico de páginas a mover
        if (typeof direction === 'number' && Math.abs(direction) > 1) {
            let newPage = direction;
            if (newPage >= totalPages) newPage = totalPages - 1;
            if (newPage < 0) newPage = 0;
            
            const actualDirection = newPage > currentPage ? 1 : -1;
            currentPage = newPage;
            mostrarSugerencias(currentPage, actualDirection);
        } else {
            // Calcular la nueva página
            let newPage = currentPage + direction;
            
            // Manejar los límites de páginas
            if (newPage >= totalPages) {
                newPage = 0; // Volver al inicio
            } else if (newPage < 0) {
                newPage = totalPages - 1; // Ir al final
            }
            
            // Si no hay cambio, no hacer nada
            if (newPage === currentPage) return;
            
            currentPage = newPage;
            
            // Mostrar las sugerencias de la nueva página con animación
            mostrarSugerencias(currentPage, direction);
        }
        
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
                    indicator.setAttribute('data-page', i);
                    indicator.addEventListener('click', () => {
                        if (!isAnimating && i !== currentPage) {
                            cambiarSugerencias(i - currentPage);
                        }
                    });
                    paginationContainer.appendChild(indicator);
                }
                
                // Mostrar la página actual
                mostrarSugerencias(currentPage, 0);
            }
        }
    });
    
    // Añadir estilos para los nuevos elementos
    const style = document.createElement('style');
    style.textContent = `
        .carousel-animation-container {
            position: relative;
            width: 100%;
            overflow: hidden;
        }
        
        .carrusel-sugerencias {
            display: flex;
            gap: 20px;
            transition: all 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            width: 100%;
            flex-wrap: nowrap;
        }
        
        .carrusel-sugerencias.nuevo {
            position: absolute;
            top: 0;
            left: 0;
            opacity: 0;
        }
        
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
        
        .card-glow-effect {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border-radius: 10px;
            box-shadow: 0 0 30px rgba(52, 152, 219, 0.5);
            opacity: 0;
            animation: glow-pulse 1s ease-out;
            pointer-events: none;
            z-index: -1;
        }
        
        @keyframes glow-pulse {
            0% {
                opacity: 0;
                transform: scale(0.8);
            }
            50% {
                opacity: 0.8;
                transform: scale(1.05);
            }
            100% {
                opacity: 0;
                transform: scale(1.1);
            }
        }
    `;
    
    document.head.appendChild(style);
    
    // Iniciar el carrusel
    mostrarSugerencias(0, 0);
    updatePagination();
    
    // Iniciar el cambio automático
    autoChangeInterval = setInterval(() => {
        cambiarSugerencias(1);
    }, 5000);
});
