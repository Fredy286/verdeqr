document.addEventListener("DOMContentLoaded", function () {
    // Ejemplo: Mostrar/ocultar menú en dispositivos móviles
    const menuToggle = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");

    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", function () {
            sidebar.classList.toggle("active");
        });
    }
});