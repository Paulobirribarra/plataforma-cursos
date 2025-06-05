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
    # URLs para cursos de recompensa
    path("cursos-bienvenida/", views.welcome_courses, name="welcome_courses"),
    path("reclamar-curso/<int:course_id>/", views.claim_reward_course, name="claim_reward_course"),
    path("saltar-bienvenida/", views.skip_welcome_courses, name="skip_welcome_courses"),
]
