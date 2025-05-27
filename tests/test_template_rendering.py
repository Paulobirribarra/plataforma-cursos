from django.test import TestCase
from django.template import Template, Context
from django.template.loader import get_template

class TemplateRenderingTest(TestCase):
    """Prueba que verifica que las plantillas se rendericen correctamente."""
    
    def test_purchase_success_template(self):
        """Prueba que la plantilla de éxito de compra se renderice correctamente."""
        try:
            template = get_template('pagos/purchase_success_fixed.html')
            print("✅ Plantilla cargada correctamente")
            
            # Prueba con un contexto básico para simular los datos necesarios
            context = {
                'payment': {'id': 123, 'amount': 59980},
                'purchased_items': [
                    {
                        'item_type': 'course',
                        'course_title': 'Curso de Prueba',
                        'membership_name': None,
                        'price_applied': 19990.0
                    }
                ],
                'has_new_membership': True,
                'has_new_courses': True,
                'total_amount': 59980.0,
            }
            
            # Intentar renderizar la plantilla
            try:
                rendered = template.render(context)
                print("✅ Plantilla renderizada correctamente")
                self.assertTrue(True)
            except Exception as e:
                print(f"❌ Error al renderizar la plantilla: {e}")
                self.fail(f"Error al renderizar la plantilla: {e}")
        
        except Exception as e:
            print(f"❌ Error al cargar la plantilla: {e}")
            self.fail(f"Error al cargar la plantilla: {e}")
