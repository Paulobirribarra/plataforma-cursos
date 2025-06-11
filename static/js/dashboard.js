/**
 * Dashboard General JavaScript
 * Funcionalidad general del dashboard (sin newsletter)
 */

// Función para ocultar notificación de beneficios
function hideBenefitNotification() {
  const notification = document.querySelector('[data-reward-notification]');
  if (notification) {
    notification.style.transition = 'all 0.5s ease-out';
    notification.style.opacity = '0';
    notification.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
      notification.style.display = 'none';
    }, 500);
    
    // Guardar en localStorage para no mostrar por un tiempo
    localStorage.setItem('rewardCoursesHidden', Date.now().toString());
  }
}

// Modal para buscar pagos por ID
function showPaymentSearchModal() {
  const modal = document.getElementById('paymentSearchModal');
  if (modal) {
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    document.getElementById('paymentIdInput').focus();
  }
}

function hidePaymentSearchModal() {
  const modal = document.getElementById('paymentSearchModal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
    document.getElementById('paymentIdInput').value = '';
  }
}

function searchPayment() {
  const paymentId = document.getElementById('paymentIdInput').value.trim();
  if (paymentId) {
    window.location.href = `/pagos/payment-status/${paymentId}/`;
  } else {
    alert('Por favor, ingresa un ID de pago válido');
  }
}

// Verificar notificaciones ocultas al cargar
document.addEventListener('DOMContentLoaded', function() {
  // Verificar si el usuario ocultó la notificación recientemente (últimas 24 horas)
  const hiddenTime = localStorage.getItem('rewardCoursesHidden');
  if (hiddenTime) {
    const hoursSinceHidden = (Date.now() - parseInt(hiddenTime)) / (1000 * 60 * 60);
    if (hoursSinceHidden < 24) {
      const notification = document.querySelector('[data-reward-notification]');
      if (notification) {
        notification.style.display = 'none';
      }
    }
  }

  // Cerrar modal con ESC
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      hidePaymentSearchModal();
    }
  });
});
