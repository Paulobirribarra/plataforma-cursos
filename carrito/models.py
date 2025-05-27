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

    def __str__(self):
        return f"Carrito de {self.user.email} ({'Activo' if self.is_active else 'Cerrado'})"


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
