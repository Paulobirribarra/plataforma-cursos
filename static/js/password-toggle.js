/**
 * Sistema Reutilizable de Toggle de Contraseña
 * Para uso en login, registro y otras páginas con campos de contraseña
 */

class PasswordToggle {
    constructor() {
        this.init();
    }

    init() {
        // Buscar todos los campos de contraseña que necesiten toggle
        const passwordFields = document.querySelectorAll('input[type="password"]');
        
        passwordFields.forEach((field, index) => {
            this.addToggleToField(field, index);
        });
    }

    addToggleToField(passwordField, index) {
        // Verificar si ya tiene un toggle
        if (passwordField.parentElement.querySelector('.password-toggle-btn')) {
            return;
        }

        // Crear el botón toggle
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.className = 'password-toggle-btn absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors duration-300';
        toggleButton.setAttribute('aria-label', 'Mostrar/Ocultar contraseña');
        
        // IDs únicos para los iconos
        const eyeClosedId = `eye-closed-${index}`;
        const eyeOpenId = `eye-open-${index}`;
        
        toggleButton.innerHTML = `
            <!-- Ojo cerrado (mostrar por defecto) -->
            <svg id="${eyeClosedId}" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
            <!-- Ojo abierto (oculto por defecto) -->
            <svg id="${eyeOpenId}" class="h-5 w-5 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
            </svg>
        `;

        // Verificar que el campo esté en un contenedor relativo
        if (!passwordField.parentElement.classList.contains('relative')) {
            passwordField.parentElement.classList.add('relative');
        }

        // Agregar el botón al contenedor del campo
        passwordField.parentElement.appendChild(toggleButton);

        // Ajustar el padding del campo para hacer espacio al botón
        if (!passwordField.classList.contains('pr-10')) {
            passwordField.classList.add('pr-10');
        }

        // Configurar el event listener
        this.setupToggleListener(toggleButton, passwordField, eyeClosedId, eyeOpenId);
    }

    setupToggleListener(toggleButton, passwordField, eyeClosedId, eyeOpenId) {
        const eyeClosed = document.getElementById(eyeClosedId);
        const eyeOpen = document.getElementById(eyeOpenId);

        toggleButton.addEventListener('click', (e) => {
            e.preventDefault();
            
            if (passwordField.type === 'password') {
                // Mostrar contraseña
                passwordField.type = 'text';
                eyeClosed.classList.add('hidden');
                eyeOpen.classList.remove('hidden');
                toggleButton.setAttribute('aria-label', 'Ocultar contraseña');
            } else {
                // Ocultar contraseña
                passwordField.type = 'password';
                eyeClosed.classList.remove('hidden');
                eyeOpen.classList.add('hidden');
                toggleButton.setAttribute('aria-label', 'Mostrar contraseña');
            }
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    new PasswordToggle();
});

// Función para inicializar toggles en campos agregados dinámicamente
window.initPasswordToggles = function() {
    new PasswordToggle();
};
