// Script para asegurar que el contenido se adapte a pantallas muy grandes
document.addEventListener('DOMContentLoaded', function() {
    // Aplicar animaciones a las tarjetas de sugerencias basadas en data-delay
    const sugerenciaCards = document.querySelectorAll('.sugerencia-card[data-delay]');
    sugerenciaCards.forEach(card => {
        const delay = card.getAttribute('data-delay');
        if (delay) {
            card.style.animation = `fadeIn 0.5s ease forwards ${delay}s`;
        }
    });
    
    // Función para ajustar el ancho de los contenedores en pantallas muy grandes
    function adjustContainersForLargeScreens() {
        const windowWidth = window.innerWidth;
        
        // Elementos que deben ocupar todo el ancho de la pantalla
        const fullWidthElements = [
            document.querySelector('.header-principal'),
            document.querySelector('.bienvenida'),
            document.querySelector('.arboles-destacados'),
            document.querySelector('.centros'),
            document.querySelector('.sugerencias'),
            document.querySelector('.footer-principal')
        ];
        
        // Elementos con ancho máximo
        const maxWidthElements = [
            document.querySelector('.header-container'),
            document.querySelector('.contenido-bienvenida'),
            document.querySelector('.titulo-seccion'),
            document.querySelector('.grid-arboles'),
            document.querySelector('.info-centros'),
            document.querySelector('.grid-centros'),
            document.querySelector('.contenedor-sugerencias'),
            document.querySelector('.contenido-footer'),
            document.querySelector('.carrusel-container')
        ];
        
        // Aplicar estilos para pantallas muy grandes
        if (windowWidth > 1400) {
            // Ancho para contenedores en pantallas muy grandes
            let maxWidth = windowWidth > 2400 ? '2200px' : 
                          windowWidth > 1800 ? '1700px' : 
                          '90vw';
            
            // Aplicar ancho completo
            fullWidthElements.forEach(el => {
                if (el) {
                    el.style.width = '100vw';
                    el.style.maxWidth = '100vw';
                    el.style.left = '0';
                    el.style.right = '0';
                }
            });
            
            // Aplicar ancho máximo
            maxWidthElements.forEach(el => {
                if (el) {
                    el.style.width = '100%';
                    el.style.maxWidth = maxWidth;
                }
            });
        }
    }
    
    // Ejecutar al cargar y cuando cambie el tamaño de la ventana
    adjustContainersForLargeScreens();
    window.addEventListener('resize', adjustContainersForLargeScreens);
});
