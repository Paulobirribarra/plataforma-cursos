from django.db import models
from django.conf import settings
from cursos.models import Course
from membresias.models import MembershipPlan


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Campos para descuentos aplicados (usando ID para evitar problemas de dependencias)
    applied_discount_code_id = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="ID del código de descuento aplicado"
    )
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Monto de descuento aplicado"
    )

    def __str__(self):
        return f"Carrito de {self.user.email} ({'Activo' if self.is_active else 'Cerrado'})"
    
    def get_applied_discount_code(self):
        """Obtiene el código de descuento aplicado"""
        if self.applied_discount_code_id:
            try:
                from cursos.models import DiscountCode
                return DiscountCode.objects.get(id=self.applied_discount_code_id)
            except DiscountCode.DoesNotExist:
                return None
        return None
    
    def get_subtotal(self):
        """Calcula el subtotal sin descuentos"""
        return sum(item.price_applied for item in self.items.all())
    
    def get_total(self):
        """Calcula el total con descuentos aplicados"""
        subtotal = self.get_subtotal()
        return max(subtotal - self.discount_amount, 0)
    
    def apply_discount_code(self, code):
        """Aplica un código de descuento al carrito"""
        try:
            from cursos.models import DiscountCode
            discount_code = DiscountCode.objects.get(code__iexact=code)
            
            # Verificar que el código es válido para al menos un curso en el carrito
            course_items = self.items.filter(item_type='course')
            valid_courses = []
            
            for item in course_items:
                if item.course == discount_code.course:
                    valid_courses.append(item)
            
            if not valid_courses:
                return False, "Este código de descuento no es válido para ningún curso en tu carrito."
            
            # Calcular el descuento
            discount_amount = 0
            for item in valid_courses:
                item_discount = (item.price_applied * discount_code.discount_percentage) / 100
                discount_amount += item_discount
            
            self.applied_discount_code_id = discount_code.id
            self.discount_amount = discount_amount
            self.save()
            
            return True, f"Código aplicado. Descuento de ${discount_amount:,.0f} CLP"
            
        except Exception as e:
            return False, "El código de descuento no existe."
    
    def remove_discount(self):
        """Remueve el descuento aplicado"""
        self.applied_discount_code_id = None
        self.discount_amount = 0
        self.save()


class CartItem(models.Model):
    CART_ITEM_TYPE = [
        ("course", "Curso"),
        ("membership", "Membresía"),
    ]
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=20, choices=CART_ITEM_TYPE)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.CASCADE)
    membership_plan = models.ForeignKey(
        MembershipPlan, null=True, blank=True, on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    price_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.item_type == "course" and self.course:
            return f"Curso: {self.course.title}"
        elif self.item_type == "membership" and self.membership_plan:
            return f"Membresía: {self.membership_plan.name}"
        return "Item desconocido"

    class Meta:
        unique_together = [("cart", "course", "membership_plan", "item_type")]
