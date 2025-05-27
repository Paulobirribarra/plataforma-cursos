from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from pagos.models import Payment

User = get_user_model()

class PurchaseSuccessViewTest(TestCase):
    """Prueba que verifica el funcionamiento de la vista purchase_success."""
    
    def setUp(self):
        """Configuración inicial para las pruebas."""        # Crear un usuario de prueba
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123',
        )
        
        # Crear un pago de prueba
        self.payment = Payment.objects.create(
            user=self.user,
            amount=59980,
            description="Test payment",
            status="completed",
            payment_type="cart"
        )
        
        # Cliente con autenticación
        self.client = Client()
        self.client.force_login(self.user)
        
    def test_purchase_success_view(self):
        """Prueba que la vista purchase_success funcione correctamente."""
        # Configurar datos de sesión necesarios
        session = self.client.session
        session['purchase_success_data'] = {
            'payment_id': self.payment.id,
            'purchased_items': [
                {
                    'item_type': 'course',
                    'course_title': 'Curso de Prueba',
                    'membership_name': None,
                    'price_applied': 19990.0
                },
                {
                    'item_type': 'membership',
                    'course_title': None,
                    'membership_name': 'Plan Básico',
                    'price_applied': 39990.0
                }
            ],
            'has_new_membership': True,
            'has_new_courses': True,
            'total_amount': 59980.0
        }
        session.save()
        
        # Llamar a la vista
        response = self.client.get(reverse('pagos:purchase_success'))
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pagos/purchase_success_fixed.html')
