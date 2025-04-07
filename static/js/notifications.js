// Función para mostrar notificaciones normales
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.querySelector('.notification-container') || createNotificationContainer();
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icon = getIconForType(type);
    const title = getTitleForType(type);
    
    notification.innerHTML = `
        <div class="notification-icon">${icon}</div>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close">&times;</button>
    `;
    
    container.appendChild(notification);
    
    // Cerrar notificación al hacer clic en el botón
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        notification.classList.add('slide-out');
        setTimeout(() => notification.remove(), 500);
    });
    
    // Cerrar automáticamente después de la duración especificada
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.add('slide-out');
                setTimeout(() => notification.remove(), 500);
            }
        }, duration);
    }
}

// Función para mostrar notificaciones modales
function showModalNotification(title, message, type = 'info', icon = null) {
    const modal = document.createElement('div');
    modal.className = 'modal-notification';
    
    let iconHtml;
    if (icon) {
        iconHtml = `<i class="${icon}"></i>`;
    } else {
        iconHtml = getIconForType(type);
    }
    
    modal.innerHTML = `
        <div class="modal-notification-content">
            <div class="modal-notification-icon">${iconHtml}</div>
            <div class="modal-notification-title">${title}</div>
            <div class="modal-notification-message">${message}</div>
            <button class="modal-notification-button">Aceptar</button>
        </div>
    `;
    
    // Asegurarse de que Font Awesome esté cargado
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const fontAwesomeLink = document.createElement('link');
        fontAwesomeLink.rel = 'stylesheet';
        fontAwesomeLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
        document.head.appendChild(fontAwesomeLink);
    }
    
    document.body.appendChild(modal);
    
    // Cerrar modal al hacer clic en el botón
    const button = modal.querySelector('.modal-notification-button');
    button.addEventListener('click', () => {
        modal.remove();
    });
}

// Función auxiliar para crear el contenedor de notificaciones
function createNotificationContainer() {
    const container = document.createElement('div');
    container.className = 'notification-container';
    document.body.appendChild(container);
    return container;
}

// Función auxiliar para obtener el ícono según el tipo
function getIconForType(type) {
    const icons = {
        success: '<i class="fas fa-check-circle"></i>',
        error: '<i class="fas fa-exclamation-circle"></i>',
        warning: '<i class="fas fa-exclamation-triangle"></i>',
        info: '<i class="fas fa-info-circle"></i>'
    };
    return icons[type] || icons.info;
}

// Función auxiliar para obtener el título según el tipo
function getTitleForType(type) {
    const titles = {
        success: 'Éxito',
        error: 'Error',
        warning: 'Advertencia',
        info: 'Información'
    };
    return titles[type] || titles.info;
}

// Función para mostrar notificación de error
function showError(message, duration = 5000) {
    showNotification(message, 'error', duration);
}

// Función para mostrar notificación de éxito
function showSuccess(message, duration = 5000) {
    showNotification(message, 'success', duration);
}

// Función para mostrar notificación de advertencia
function showWarning(message, duration = 5000) {
    showNotification(message, 'warning', duration);
}

// Función para mostrar notificación de información
function showInfo(message, duration = 5000) {
    showNotification(message, 'info', duration);
}

// Función para mostrar modal de error
function showErrorModal(title, message) {
    showModalNotification(title, message, 'error');
}

// Función para mostrar modal de éxito
function showSuccessModal(title, message) {
    showModalNotification(title, message, 'success');
}

// Función para mostrar modal de advertencia
function showWarningModal(title, message) {
    showModalNotification(title, message, 'warning');
}

// Función para mostrar modal de información
function showInfoModal(title, message) {
    showModalNotification(title, message, 'info');
}

// Función para manejar mensajes flash
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        const type = message.dataset.type || 'info';
        showNotification(message.textContent, type);
        message.remove();
    });
});

// Función para manejar respuestas AJAX
function handleAjaxResponse(response) {
    if (response.success) {
        showNotification(response.message, 'success');
        if (response.redirect) {
            window.location.href = response.redirect;
        }
    } else {
        showNotification(response.message, 'danger');
    }
} 