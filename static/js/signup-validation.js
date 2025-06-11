/**
 * Sistema de Validación Avanzado para Registro de Usuario
 * Incluye: Validación AJAX de email, toggles de contraseña, validación en tiempo real
 */
class SignupValidator {
    constructor() {
        this.emailCheckTimeout = null;
        this.isEmailValid = false;
        this.lastCheckedEmail = '';
        
        this.initializeElements();
        this.setupEventListeners();
        this.initializeExistingValues();
        
        console.log('Sistema de registro mejorado inicializado');
    }

    initializeElements() {
        // === ELEMENTOS DEL DOM ===
        this.form = document.querySelector('form');
        this.emailInput = document.getElementById('id_email');
        this.password1 = document.getElementById('id_password1');
        this.password2 = document.getElementById('id_password2');
        this.signupButton = document.getElementById('signup-button');
        this.passwordMatchIndicator = document.getElementById('password-match-indicator');
        this.passwordMatchText = document.getElementById('password-match-text');
        
        // Elementos para validación de email
        this.emailSpinner = document.getElementById('email-check-spinner');
        this.emailSuccess = document.getElementById('email-check-success');
        this.emailError = document.getElementById('email-check-error');
        this.emailValidationMessage = document.getElementById('email-validation-message');
        this.emailMessageContent = document.getElementById('email-message-content');
        this.emailMessageText = document.getElementById('email-message-text');
          // Debug: verificar si los elementos existen
        console.log('Email input encontrado:', !!this.emailInput);
        console.log('Email spinner encontrado:', !!this.emailSpinner);
        console.log('Email success encontrado:', !!this.emailSuccess);
        console.log('Email error encontrado:', !!this.emailError);
        
        // Los elementos de toggle son manejados por password-toggle.js
        
        // Elementos de validación visual de contraseñas
        this.checks = {
            length: document.getElementById('length-check'),
            uppercase: document.getElementById('uppercase-check'),
            lowercase: document.getElementById('lowercase-check'),
            number: document.getElementById('number-check'),
            special: document.getElementById('special-check')
        };
    }

    setupEventListeners() {        // Event listeners para validación de email
        if (this.emailInput) {
            this.emailInput.addEventListener('input', (e) => this.handleEmailInput(e));
        }

        // Event listeners para validación de contraseñas
        if (this.password1) {
            this.password1.addEventListener('input', (e) => this.handlePassword1Input(e));
        }
        
        if (this.password2) {
            this.password2.addEventListener('input', () => this.checkPasswordMatch());
        }

        // Los toggles de contraseña son manejados por password-toggle.js

        // Event listener para validación del formulario
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }

    // === FUNCIONES DE UTILIDAD ===
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // === VALIDACIÓN DE EMAIL AJAX ===
    handleEmailInput(e) {
        const email = e.target.value.trim();
        
        // Limpiar timeout anterior
        if (this.emailCheckTimeout) {
            clearTimeout(this.emailCheckTimeout);
        }
        
        // Limpiar indicadores si el campo está vacío
        if (!email) {
            this.hideAllEmailIndicators();
            this.removeEmailStyling();
            this.isEmailValid = false;
            return;
        }
        
        // Verificar después de 500ms de inactividad
        this.emailCheckTimeout = setTimeout(() => {
            this.checkEmailAvailability(email);
        }, 500);
    }

    async checkEmailAvailability(email) {
        if (!email || email === this.lastCheckedEmail) return;
        
        console.log('Verificando email:', email);
        this.lastCheckedEmail = email;
        
        // Validar formato básico de email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            console.log('Email formato inválido');
            this.showEmailError('Formato de email inválido');
            return;
        }
        
        // Mostrar spinner
        this.hideAllEmailIndicators();
        if (this.emailSpinner) {
            this.emailSpinner.style.display = 'block';
        }
        
        console.log('Enviando petición AJAX a:', '/usuarios/check-email/');
        
        try {
            const response = await fetch('/usuarios/check-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({ email: email })
            });
            
            console.log('Respuesta recibida:', response.status);
            const data = await response.json();
            console.log('Datos recibidos:', data);
            
            this.hideAllEmailIndicators();
            
            if (data.available) {
                this.showEmailSuccess('Email disponible');
                this.isEmailValid = true;
            } else {
                this.showEmailError('Este email ya está registrado');
                this.isEmailValid = false;
            }
        } catch (error) {
            console.error('Error en petición AJAX:', error);
            this.hideAllEmailIndicators();
            this.showEmailError('Error verificando disponibilidad');
            this.isEmailValid = false;
        }
    }
    
    hideAllEmailIndicators() {
        if (this.emailSpinner) this.emailSpinner.style.display = 'none';
        if (this.emailSuccess) this.emailSuccess.style.display = 'none';
        if (this.emailError) this.emailError.style.display = 'none';
        if (this.emailValidationMessage) this.emailValidationMessage.style.display = 'none';
    }
    
    showEmailSuccess(message) {
        if (this.emailSuccess) this.emailSuccess.style.display = 'block';
        if (this.emailValidationMessage) this.emailValidationMessage.style.display = 'block';
        if (this.emailMessageContent) this.emailMessageContent.className = 'flex items-center text-green-600';
        if (this.emailMessageText) this.emailMessageText.textContent = message;
        
        // Actualizar estilo del campo
        this.emailInput.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
        this.emailInput.classList.add('border-green-500', 'focus:border-green-500', 'focus:ring-green-500');
    }
    
    showEmailError(message) {
        if (this.emailError) this.emailError.style.display = 'block';
        if (this.emailValidationMessage) this.emailValidationMessage.style.display = 'block';
        if (this.emailMessageContent) this.emailMessageContent.className = 'flex items-center text-red-600';
        if (this.emailMessageText) this.emailMessageText.textContent = message;
        
        // Actualizar estilo del campo
        this.emailInput.classList.remove('border-green-500', 'focus:border-green-500', 'focus:ring-green-500');
        this.emailInput.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
    }

    removeEmailStyling() {
        this.emailInput.classList.remove(
            'border-red-500', 'border-green-500', 
            'focus:border-red-500', 'focus:border-green-500', 
            'focus:ring-red-500', 'focus:ring-green-500'
        );
    }    // === VALIDACIÓN DE CONTRASEÑAS ===
    validatePassword(value) {
        return {
            length: value.length >= 8,
            uppercase: /[A-Z]/.test(value),
            lowercase: /[a-z]/.test(value),
            number: /[0-9]/.test(value),
            special: /[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]/.test(value)
        };
    }
    
    updatePasswordChecks(validations) {
        Object.keys(validations).forEach(key => {
            const checkElement = this.checks[key];
            if (!checkElement) return;
            
            const icon = checkElement.querySelector('svg');
            const text = checkElement.querySelector('span');
            
            if (validations[key]) {
                icon.classList.remove('text-gray-400');
                icon.classList.add('text-green-500');
                text.classList.remove('text-gray-600');
                text.classList.add('text-green-700');
            } else {
                icon.classList.remove('text-green-500');
                icon.classList.add('text-gray-400');
                text.classList.remove('text-green-700');
                text.classList.add('text-gray-600');
            }
        });
    }
    
    handlePassword1Input(e) {
        const validations = this.validatePassword(e.target.value);
        this.updatePasswordChecks(validations);
        
        // Actualizar estilo del campo
        const allValid = Object.values(validations).every(v => v);
        if (e.target.value.length > 0) {
            if (allValid) {
                e.target.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
                e.target.classList.add('border-green-500', 'focus:border-green-500', 'focus:ring-green-500');
            } else {
                e.target.classList.remove('border-green-500', 'focus:border-green-500', 'focus:ring-green-500');
            }
        }
        
        // Verificar coincidencia con password2 si tiene contenido
        if (this.password2 && this.password2.value.length > 0) {
            this.checkPasswordMatch();
        }
    }
    
    checkPasswordMatch() {
        const match = this.password1.value === this.password2.value && this.password1.value.length > 0;
        
        if (this.password2.value.length > 0) {
            if (this.passwordMatchIndicator) this.passwordMatchIndicator.style.display = 'block';
            
            if (match) {
                this.password2.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
                this.password2.classList.add('border-green-500', 'focus:border-green-500', 'focus:ring-green-500');
                
                const icon = this.passwordMatchIndicator?.querySelector('svg');
                if (icon) {
                    icon.classList.remove('text-red-500');
                    icon.classList.add('text-green-500');
                }
                
                if (this.passwordMatchText) {
                    this.passwordMatchText.classList.remove('text-red-600');
                    this.passwordMatchText.classList.add('text-green-600');
                    this.passwordMatchText.textContent = 'Las contraseñas coinciden';
                }
            } else {
                this.password2.classList.remove('border-green-500', 'focus:border-green-500', 'focus:ring-green-500');
                this.password2.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
                
                const icon = this.passwordMatchIndicator?.querySelector('svg');
                if (icon) {
                    icon.classList.remove('text-green-500');
                    icon.classList.add('text-red-500');
                }
                
                if (this.passwordMatchText) {
                    this.passwordMatchText.classList.remove('text-green-600');
                    this.passwordMatchText.classList.add('text-red-600');
                    this.passwordMatchText.textContent = 'Las contraseñas no coinciden';
                }
            }
        } else {
            if (this.passwordMatchIndicator) this.passwordMatchIndicator.style.display = 'none';
            this.password2.classList.remove(
                'border-red-500', 'border-green-500', 
                'focus:border-red-500', 'focus:border-green-500', 
                'focus:ring-red-500', 'focus:ring-green-500'
            );
        }
    }
    
    // === VALIDACIÓN DEL FORMULARIO ===
    handleFormSubmit(e) {
        // Verificar validación de email
        if (!this.isEmailValid && this.emailInput.value.trim()) {
            e.preventDefault();
            this.showErrorMessage('Por favor, utiliza un email válido y disponible.');
            this.emailInput.focus();
            return;
        }
        
        // Verificar validaciones de contraseña
        const validations = this.validatePassword(this.password1.value);
        const passwordMatch = this.password1.value === this.password2.value && this.password1.value.length > 0;
        const allFieldsValid = Object.values(validations).every(v => v) && passwordMatch;
        
        if (!allFieldsValid) {
            e.preventDefault();
            
            // Crear mensaje de error detallado
            let errorMessage = 'Por favor, corrige los siguientes errores:';
            const errors = [];
            
            if (!validations.length) errors.push('La contraseña debe tener al menos 8 caracteres');
            if (!validations.uppercase) errors.push('La contraseña debe contener al menos una letra mayúscula');
            if (!validations.lowercase) errors.push('La contraseña debe contener al menos una letra minúscula');
            if (!validations.number) errors.push('La contraseña debe contener al menos un número');
            if (!validations.special) errors.push('La contraseña debe contener al menos un carácter especial');
            if (!passwordMatch) errors.push('Las contraseñas no coinciden');
            
            if (errors.length > 0) {
                errorMessage += '<ul class="list-disc ml-5 mt-2">';
                errors.forEach(error => {
                    errorMessage += `<li>${error}</li>`;
                });
                errorMessage += '</ul>';
                
                this.showErrorMessage(errorMessage);
                
                // Hacer scroll al principio del formulario
                const formContainer = document.querySelector('.lg\\:col-span-3');
                if (formContainer) {
                    formContainer.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                }
            }
        }
    }
    
    // === FUNCIONES DE INTERFAZ ===
    showErrorMessage(message) {
        // Remover mensaje de error existente
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Crear nuevo mensaje de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message flex items-start p-4 mb-6 text-sm text-red-800 bg-red-50 border border-red-200 rounded-lg';
        errorDiv.innerHTML = `
            <svg class="flex-shrink-0 inline w-4 h-4 mr-3 mt-0.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z"/>
            </svg>
            <div>
                <span class="font-medium">${message}</span>
            </div>
        `;
        
        // Insertar antes del formulario
        const formContainer = document.querySelector('.bg-white.rounded-2xl.shadow-xl');
        if (formContainer) {
            formContainer.insertBefore(errorDiv, formContainer.firstChild);
        }
    }
    
    // === INICIALIZACIÓN ===
    initializeExistingValues() {
        // Inicializar validaciones si hay contenido previo
        if (this.password1 && this.password1.value) {
            const validations = this.validatePassword(this.password1.value);
            this.updatePasswordChecks(validations);
        }
        
        if (this.password2 && this.password2.value) {
            this.checkPasswordMatch();
        }
        
        if (this.emailInput && this.emailInput.value.trim()) {
            this.checkEmailAvailability(this.emailInput.value.trim());
        }
    }
}

// Inicializar el validador cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    new SignupValidator();
});