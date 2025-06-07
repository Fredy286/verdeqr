// animations.js - Script para mejorar las animaciones de la página principal

document.addEventListener('DOMContentLoaded', function() {
    // Aplicar índices a los elementos para animaciones escalonadas
    applyStaggeredAnimations('.arbol-card', 'fadeInUp');
    applyStaggeredAnimations('.centro-card', 'fadeInUp');

    // Mejorar las animaciones de las tarjetas de sugerencias
    enhanceSuggestionCards();

    // Aplicar efecto de hover a los botones
    enhanceButtons();
});

// Función para aplicar animaciones escalonadas a elementos
function applyStaggeredAnimations(selector, animationName) {
    const elements = document.querySelectorAll(selector);
    elements.forEach((el, index) => {
        // Establecer un índice para cada elemento (para el retraso de la animación)
        el.style.setProperty('--item-index', index);

        // Aplicar la clase de animación
        el.classList.add(animationName);

        // Observar cuando el elemento entra en el viewport
        observeElement(el);
    });
}

// Función para observar cuando un elemento entra en el viewport
function observeElement(element) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Cuando el elemento es visible, activar la animación
                entry.target.style.opacity = '1';
                // Dejar de observar después de activar
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 }); // Activar cuando al menos el 10% del elemento es visible

    observer.observe(element);
}

// Función para mejorar las animaciones de las tarjetas de sugerencias
function enhanceSuggestionCards() {
    const cards = document.querySelectorAll('.sugerencia-card');

    cards.forEach((card, index) => {
        // Asegurarse de que las tarjetas sean visibles
        card.style.opacity = '1';
        card.style.transform = 'none';

        // Aplicar una animación de entrada más sofisticada
        card.style.animation = `fadeIn 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards ${index * 0.15}s`;

        // Asegurarse de que la tarjeta sea visible después de la animación
        setTimeout(() => {
            card.style.opacity = '1';

            // Añadir efecto de brillo sutil al aparecer
            const glowEffect = document.createElement('div');
            glowEffect.className = 'card-glow-effect';
            card.appendChild(glowEffect);

            setTimeout(() => {
                if (glowEffect && glowEffect.parentNode === card) {
                    card.removeChild(glowEffect);
                }
            }, 1000);
        }, index * 150 + 700);

        // Añadir interactividad a los elementos internos
        const userIcon = card.querySelector('.usuario-info i');
        const dateIcon = card.querySelector('.fecha i');
        const content = card.querySelector('.sugerencia-contenido');

        if (userIcon) {
            userIcon.style.transition = 'transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        }

        if (dateIcon) {
            dateIcon.style.transition = 'transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        }

        if (content) {
            content.style.transition = 'color 0.3s ease, transform 0.3s ease';
        }

        // Añadir efecto de ondas al hacer clic
        card.addEventListener('click', function(e) {
            const ripple = document.createElement('div');
            ripple.className = 'card-ripple';

            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            this.appendChild(ripple);

            setTimeout(() => {
                if (ripple && ripple.parentNode === this) {
                    this.removeChild(ripple);
                }
            }, 600);
        });
    });

    // Si no hay tarjetas, asegurarse de que el mensaje 'sin sugerencias' sea visible
    const sinSugerencias = document.querySelector('.sin-sugerencias');
    if (sinSugerencias) {
        sinSugerencias.style.opacity = '1';
        sinSugerencias.style.display = 'block';
    }

    // Añadir estilos para los nuevos efectos
    const style = document.createElement('style');
    style.textContent = `
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

        .card-ripple {
            position: absolute;
            border-radius: 50%;
            background-color: rgba(52, 152, 219, 0.3);
            width: 100px;
            height: 100px;
            margin-top: -50px;
            margin-left: -50px;
            animation: ripple-effect 0.6s ease-out;
            opacity: 0;
            pointer-events: none;
            z-index: 10;
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

        @keyframes ripple-effect {
            0% {
                transform: scale(0);
                opacity: 0.5;
            }
            100% {
                transform: scale(3);
                opacity: 0;
            }
        }
    `;

    document.head.appendChild(style);
}

// Función para mejorar los botones
function enhanceButtons() {
    const buttons = document.querySelectorAll('.btn, .btn-enviar');

    buttons.forEach(btn => {
        // Añadir efecto de ondas al hacer clic
        btn.addEventListener('click', function(e) {
            // Crear elemento de onda
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');

            // Posicionar la onda en el punto de clic
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            // Añadir la onda al botón
            this.appendChild(ripple);

            // Eliminar la onda después de la animación
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}
