document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchForm = document.getElementById('searchForm');
    
    if (!searchInput) return;
    
    // Crear el contenedor de sugerencias
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions';
    suggestionsContainer.style.display = 'none';
    searchForm.appendChild(suggestionsContainer);
    
    // Estilo para el contenedor de sugerencias
    suggestionsContainer.style.position = 'absolute';
    suggestionsContainer.style.width = '100%';
    suggestionsContainer.style.maxHeight = '300px';
    suggestionsContainer.style.overflowY = 'auto';
    suggestionsContainer.style.backgroundColor = 'white';
    suggestionsContainer.style.border = '1px solid #ddd';
    suggestionsContainer.style.borderRadius = '0 0 5px 5px';
    suggestionsContainer.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
    suggestionsContainer.style.zIndex = '1000';
    suggestionsContainer.style.top = '100%';
    
    // Función para obtener sugerencias
    let timeoutId;
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        // Limpiar el timeout anterior
        clearTimeout(timeoutId);
        
        // Si el campo está vacío, ocultar las sugerencias
        if (!query) {
            suggestionsContainer.style.display = 'none';
            return;
        }
        
        // Esperar 300ms después de que el usuario deje de escribir
        timeoutId = setTimeout(function() {
            // Hacer la petición AJAX
            fetch(`/api/sugerencias_busqueda?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    // Limpiar el contenedor de sugerencias
                    suggestionsContainer.innerHTML = '';
                    
                    // Si no hay sugerencias, ocultar el contenedor
                    if (data.length === 0) {
                        suggestionsContainer.style.display = 'none';
                        return;
                    }
                    
                    // Mostrar las sugerencias
                    data.forEach(suggestion => {
                        const suggestionItem = document.createElement('div');
                        suggestionItem.className = 'suggestion-item';
                        suggestionItem.textContent = suggestion;
                        suggestionItem.style.padding = '10px 15px';
                        suggestionItem.style.cursor = 'pointer';
                        suggestionItem.style.borderBottom = '1px solid #eee';
                        suggestionItem.style.transition = 'background-color 0.2s';
                        
                        // Resaltar la parte de la sugerencia que coincide con la búsqueda
                        const regex = new RegExp(`(${query})`, 'gi');
                        suggestionItem.innerHTML = suggestion.replace(regex, '<strong>$1</strong>');
                        
                        // Al hacer hover sobre una sugerencia
                        suggestionItem.addEventListener('mouseenter', function() {
                            this.style.backgroundColor = '#f5f5f5';
                        });
                        
                        // Al salir del hover
                        suggestionItem.addEventListener('mouseleave', function() {
                            this.style.backgroundColor = 'white';
                        });
                        
                        // Al hacer clic en una sugerencia
                        suggestionItem.addEventListener('click', function() {
                            searchInput.value = suggestion;
                            suggestionsContainer.style.display = 'none';
                            searchForm.submit();
                        });
                        
                        suggestionsContainer.appendChild(suggestionItem);
                    });
                    
                    // Mostrar el contenedor de sugerencias
                    suggestionsContainer.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error al obtener sugerencias:', error);
                    suggestionsContainer.style.display = 'none';
                });
        }, 300);
    });
    
    // Ocultar las sugerencias al hacer clic fuera del buscador
    document.addEventListener('click', function(event) {
        if (!searchForm.contains(event.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });
    
    // Navegación con teclado por las sugerencias
    searchInput.addEventListener('keydown', function(event) {
        const items = suggestionsContainer.querySelectorAll('.suggestion-item');
        const activeItem = suggestionsContainer.querySelector('.suggestion-item.active');
        
        // Si no hay sugerencias visibles, no hacer nada
        if (suggestionsContainer.style.display === 'none' || items.length === 0) {
            return;
        }
        
        switch (event.key) {
            case 'ArrowDown':
                event.preventDefault();
                if (!activeItem) {
                    // Si no hay elemento activo, activar el primero
                    items[0].classList.add('active');
                    items[0].style.backgroundColor = '#e0e0e0';
                } else {
                    // Obtener el índice del elemento activo
                    const currentIndex = Array.from(items).indexOf(activeItem);
                    // Desactivar el elemento actual
                    activeItem.classList.remove('active');
                    activeItem.style.backgroundColor = 'white';
                    // Activar el siguiente elemento (o el primero si estamos en el último)
                    const nextIndex = (currentIndex + 1) % items.length;
                    items[nextIndex].classList.add('active');
                    items[nextIndex].style.backgroundColor = '#e0e0e0';
                    // Asegurarse de que el elemento sea visible
                    items[nextIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
                break;
                
            case 'ArrowUp':
                event.preventDefault();
                if (!activeItem) {
                    // Si no hay elemento activo, activar el último
                    items[items.length - 1].classList.add('active');
                    items[items.length - 1].style.backgroundColor = '#e0e0e0';
                } else {
                    // Obtener el índice del elemento activo
                    const currentIndex = Array.from(items).indexOf(activeItem);
                    // Desactivar el elemento actual
                    activeItem.classList.remove('active');
                    activeItem.style.backgroundColor = 'white';
                    // Activar el elemento anterior (o el último si estamos en el primero)
                    const prevIndex = (currentIndex - 1 + items.length) % items.length;
                    items[prevIndex].classList.add('active');
                    items[prevIndex].style.backgroundColor = '#e0e0e0';
                    // Asegurarse de que el elemento sea visible
                    items[prevIndex].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
                break;
                
            case 'Enter':
                if (activeItem) {
                    event.preventDefault();
                    searchInput.value = activeItem.textContent;
                    suggestionsContainer.style.display = 'none';
                    searchForm.submit();
                }
                break;
                
            case 'Escape':
                suggestionsContainer.style.display = 'none';
                break;
        }
    });
});
