from django.contrib import admin
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__email",)
    date_hierarchy = "created_at"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "item_type",
        "course",
        "membership_plan",
        "quantity",
        "price_applied",
        "added_at",
    )
    list_filter = ("item_type", "added_at")
    search_fields = ("cart__user__email", "course__title", "membership_plan__name")
