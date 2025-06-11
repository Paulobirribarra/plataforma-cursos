/**
 * Newsletter Dashboard Manager
 * Manages all newsletter-related functionality in the dashboard
 */
class NewsletterDashboard {
    constructor() {
        this.toggle = document.getElementById('newsletter-toggle');
        this.isLoading = false;

        if (this.toggle) {
            this.initEventListeners();
        }
    }

    // Initialize event listeners
    initEventListeners() {
        this.toggle.addEventListener('change', async (e) => {
            if (this.isLoading) {
                e.preventDefault();
                return;
            }

            const isChecked = e.target.checked;
            this.setLoadingState(true);
            this.updateUIState(isChecked);

            try {
                const response = await fetch(this.getToggleURL(), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        suscrito: isChecked
                    })
                });

                const data = await response.json();

                if (data.success) {
                    this.showNotification(data.message, 'success');
                } else {
                    // Revert UI on error
                    this.toggle.checked = !isChecked;
                    this.updateUIState(!isChecked);
                    this.showNotification(data.message || 'Error al actualizar preferencias', 'error');
                }
            } catch (error) {
                console.error('Error en toggle newsletter:', error);
                // Revert UI on error
                this.toggle.checked = !isChecked;
                this.updateUIState(!isChecked);
                this.showNotification('Error de conexión. Inténtalo de nuevo.', 'error');
            } finally {
                this.setLoadingState(false);
            }
        });
    }

    // Get CSRF token
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
    }

    // Get toggle URL
    getToggleURL() {
        const container = document.querySelector('.newsletter-toggle-container');
        return container?.dataset.toggleUrl || '/usuarios/newsletter/toggle/';
    }

    // Update UI state
    updateUIState(isSubscribed) {
        const icon = document.querySelector('.newsletter-status-icon');
        const statusText = document.querySelector('.newsletter-status-text');
        const descText = document.querySelector('.newsletter-desc-text');
        const container = document.querySelector('.newsletter-status-container');

        if (container) {
            container.className = `w-16 h-16 ${isSubscribed ? 'bg-green-100' : 'bg-gray-100'} rounded-full flex items-center justify-center mx-auto mb-3`;
        }

        if (icon) {
            icon.className = `w-8 h-8 ${isSubscribed ? 'text-green-600' : 'text-gray-400'}`;
            icon.innerHTML = isSubscribed ? this.getCheckIcon() : this.getMailIcon();
        }

        if (statusText) {
            statusText.innerHTML = isSubscribed 
                ? '<span class="text-green-600">✓ Suscrito</span>'
                : '<span class="text-gray-500">No suscrito</span>';
        }

        if (descText) {
            descText.textContent = isSubscribed 
                ? 'Recibes nuestras novedades'
                : 'Únete a nuestro newsletter';
        }

        this.updateStatsSection(isSubscribed);
    }

    // Update stats section
    updateStatsSection(isSubscribed) {
        const statsDiv = document.querySelector('.newsletter-stats');
        const parentDiv = document.querySelector('.newsletter-actions')?.parentElement;

        if (isSubscribed && !statsDiv && parentDiv) {
            const newStats = document.createElement('div');
            newStats.className = 'newsletter-stats mt-4 p-3 bg-green-50 rounded-lg border border-green-200';
            newStats.innerHTML = `
                <div class="flex items-center justify-between text-sm">
                    <span class="text-green-700 font-medium">Último boletín:</span>
                    <span class="text-green-600">Hace poco</span>
                </div>
            `;
            parentDiv.appendChild(newStats);
        } else if (!isSubscribed && statsDiv) {
            statsDiv.remove();
        }
    }

    // Show notification
    showNotification(message, type = 'success') {
        this.hideAllNotifications();

        const notification = document.createElement('div');
        notification.className = `newsletter-notification ${type}`;
        notification.innerHTML = `
            <div class="flex items-center">
                <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    ${type === 'success' 
                        ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>'
                        : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>'
                    }
                </svg>
                <span class="flex-1">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" 
                        class="ml-3 text-current opacity-70 hover:opacity-100 transition-opacity">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => this.hideNotification(notification), 5000);
    }

    // Hide specific notification
    hideNotification(notification) {
        if (notification && notification.parentElement) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.parentElement.removeChild(notification);
                }
            }, 300);
        }
    }

    // Hide all notifications
    hideAllNotifications() {
        const notifications = document.querySelectorAll('.newsletter-notification');
        notifications.forEach(notification => this.hideNotification(notification));
    }

    // Get check icon SVG
    getCheckIcon() {
        return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>`;
    }

    // Get mail icon SVG
    getMailIcon() {
        return `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>`;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('newsletter-toggle')) {
        window.newsletterDashboard = new NewsletterDashboard();
    }
});

// Global compatibility function for existing template
window.toggleNewsletter = function() {
    if (window.newsletterDashboard && window.newsletterDashboard.toggle) {
        const event = new Event('change');
        window.newsletterDashboard.toggle.dispatchEvent(event);
    }
};

// Global function to show notifications
window.showNotification = function(message, type = 'success') {
    if (window.newsletterDashboard) {
        window.newsletterDashboard.showNotification(message, type);
    } else {
        alert(message);
    }
};