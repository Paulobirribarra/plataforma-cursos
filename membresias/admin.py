# membresias/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import MembershipPlan, Membership, MembershipHistory, ConsultationType, ConsultationRequest


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "courses_per_month",
        "discount_percentage",
        "is_active",
    )
    list_filter = ("is_active", "telegram_level")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "is_active")}),
        (
            _("Características"),
            {
                "fields": (
                    "price",
                    "courses_per_month",
                    "discount_percentage",
                    "consultations",
                    "telegram_level",
                    "features",
                )
            },
        ),
        (
            _("Fechas"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "status",
        "start_date",
        "end_date",
        "courses_remaining",
        "consultations_remaining",
    )
    list_filter = ("status", "plan", "auto_renew")
    search_fields = ("user__email", "user__username", "plan__name")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("user", "plan", "status")}),
        (
            _("Fechas"),
            {"fields": ("start_date", "end_date", "created_at", "updated_at")},
        ),
        (
            _("Recursos"),
            {"fields": ("courses_remaining", "consultations_remaining", "auto_renew")},
        ),
    )


@admin.register(MembershipHistory)
class MembershipHistoryAdmin(admin.ModelAdmin):
    list_display = ("membership", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("membership__user__email", "membership__plan__name")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("membership", "action", "details")}),
        (_("Fechas"), {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(ConsultationType)
class ConsultationTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_individual",
        "duration_minutes",
        "is_active",
        "get_membership_plans",
    )
    list_filter = ("is_individual", "is_active", "membership_plans")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)
    filter_horizontal = ("membership_plans",)
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "is_active")}),
        (
            _("Configuración"),
            {
                "fields": (
                    "is_individual",
                    "duration_minutes",
                    "membership_plans",
                )
            },
        ),
        (
            _("Fechas"),
            {"fields": ("created_at",), "classes": ("collapse",)},
        ),
    )

    def get_membership_plans(self, obj):
        """Muestra los planes de membresía asociados."""
        return ", ".join([plan.name for plan in obj.membership_plans.all()])
    get_membership_plans.short_description = _("Planes de membresía")


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "consultation_type",
        "requested_date",
        "status",
        "created_at",
    )
    list_filter = ("status", "consultation_type", "created_at")
    search_fields = ("user__email", "user__username", "consultation_type__name")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("user", "membership", "consultation_type")}),
        (
            _("Programación"),
            {"fields": ("requested_date", "status", "notes")},
        ),
        (
            _("Fechas"),
            {"fields": ("created_at",), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "user", "membership", "consultation_type"
        )
