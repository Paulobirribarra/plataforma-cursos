from django.urls import path
from . import views

app_name = "membresias"

urlpatterns = [
    path("", views.plan_list, name="plan_list"),
    path("plan/<slug:slug>/", views.plan_detail, name="plan_detail"),
    path(
        "comprar/<int:plan_id>/", views.purchase_membership, name="purchase_membership"
    ),
    path("mi-membresia/", views.my_membership, name="my_membership"),
    path(
        "cancelar/<int:membership_id>/",
        views.cancel_membership,
        name="cancel_membership",
    ),
]
