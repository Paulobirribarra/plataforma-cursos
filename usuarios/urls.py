#plataforma-cursos/usuarios/urls.py
from django.urls import path
from .views import dashboard, CustomSignupView

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', CustomSignupView.as_view(), name='register'),
]
