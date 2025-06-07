// Script para manejar animaciones al hacer scroll
document.addEventListener('DOMContentLoaded', function() {
    // Elementos que queremos animar al hacer scroll
    const animatedElements = document.querySelectorAll('.animate-on-scroll');

    // Función para verificar si un elemento está visible en la ventana
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8
        );
    }

    // Función para animar elementos visibles
    function animateElementsOnScroll() {
        animatedElements.forEach(element => {
            if (isElementInViewport(element) && !element.classList.contains('animated')) {
                element.classList.add('animated');
            }
        });
    }

    // Ejecutar al cargar la página y al hacer scroll
    animateElementsOnScroll();
    window.addEventListener('scroll', animateElementsOnScroll);

    // Efecto de scroll para el menú
    const menuSuperior = document.querySelector('.menu-superior');
    const navegacionRapida = document.querySelector('.navegacion-rapida');

    function handleMenuScroll() {
        if (window.scrollY > 50) {
            menuSuperior.classList.add('scrolled');
            if (navegacionRapida) {
                navegacionRapida.style.top = '55px'; // Altura del menú cuando está encogido
            }
        } else {
            menuSuperior.classList.remove('scrolled');
            if (navegacionRapida) {
                navegacionRapida.style.top = '70px'; // Altura original del menú
            }
        }
    }

    window.addEventListener('scroll', handleMenuScroll);
});
