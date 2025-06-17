// mobile-menu.js - Script para el menú hamburguesa en móviles

document.addEventListener('DOMContentLoaded', function() {
    // Crear el botón hamburguesa si no existe
    createMobileMenuButton();
    
    // Configurar eventos
    setupMobileMenu();
});

function createMobileMenuButton() {
    const headerPrincipal = document.querySelector('.header-principal');
    if (!headerPrincipal) return;
    
    // Verificar si ya existe el botón
    if (document.querySelector('.menu-toggle')) return;
    
    // Crear el botón hamburguesa
    const menuToggle = document.createElement('button');
    menuToggle.className = 'menu-toggle';
    menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
    menuToggle.setAttribute('aria-label', 'Abrir menú');
    
    // Insertar el botón al principio del header
    headerPrincipal.insertBefore(menuToggle, headerPrincipal.firstChild);
}

function setupMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const menuPrincipal = document.querySelector('.menu-principal');
    const overlay = createOverlay();
    
    if (!menuToggle || !menuPrincipal) return;
    
    // Evento para abrir/cerrar menú
    menuToggle.addEventListener('click', function() {
        toggleMenu();
    });
    
    // Cerrar menú al hacer clic en el overlay
    overlay.addEventListener('click', function() {
        closeMenu();
    });
    
    // Cerrar menú al hacer clic en un enlace del menú
    const menuLinks = menuPrincipal.querySelectorAll('a');
    menuLinks.forEach(link => {
        link.addEventListener('click', function() {
            closeMenu();
        });
    });
    
    // Cerrar menú con la tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMenu();
        }
    });
    
    // Manejar cambios de tamaño de ventana
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMenu();
        }
    });
}

function createOverlay() {
    let overlay = document.querySelector('.menu-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'menu-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 999;
            display: none;
        `;
        document.body.appendChild(overlay);
    }
    return overlay;
}

function toggleMenu() {
    const menuPrincipal = document.querySelector('.menu-principal');
    const menuToggle = document.querySelector('.menu-toggle');
    const overlay = document.querySelector('.menu-overlay');
    
    if (menuPrincipal.classList.contains('active')) {
        closeMenu();
    } else {
        openMenu();
    }
}

function openMenu() {
    const menuPrincipal = document.querySelector('.menu-principal');
    const menuToggle = document.querySelector('.menu-toggle');
    const overlay = document.querySelector('.menu-overlay');
    
    menuPrincipal.classList.add('active');
    menuToggle.innerHTML = '<i class="fas fa-times"></i>';
    menuToggle.setAttribute('aria-label', 'Cerrar menú');
    overlay.style.display = 'block';
    
    // Prevenir scroll del body
    document.body.style.overflow = 'hidden';
}

function closeMenu() {
    const menuPrincipal = document.querySelector('.menu-principal');
    const menuToggle = document.querySelector('.menu-toggle');
    const overlay = document.querySelector('.menu-overlay');
    
    if (menuPrincipal) menuPrincipal.classList.remove('active');
    if (menuToggle) {
        menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
        menuToggle.setAttribute('aria-label', 'Abrir menú');
    }
    if (overlay) overlay.style.display = 'none';
    
    // Restaurar scroll del body
    document.body.style.overflow = '';
}

// Función para detectar si estamos en móvil
function isMobile() {
    return window.innerWidth <= 768;
}

// Exportar funciones para uso externo si es necesario
window.mobileMenu = {
    toggle: toggleMenu,
    open: openMenu,
    close: closeMenu,
    isMobile: isMobile
};
