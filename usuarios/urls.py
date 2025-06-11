#plataforma-cursos/usuarios/urls.py
from django.urls import path
from .views import (
    dashboard, CustomSignupView, my_courses, check_email_available,
    newsletter_preferences, toggle_newsletter_ajax, profile_preferences
)

app_name = "usuarios"

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', CustomSignupView.as_view(), name='register'),
    path('mis-cursos/', my_courses, name='my_courses'),
    path('check-email/', check_email_available, name='check_email_available'),
    
    # Nuevas rutas para gestión de newsletter y preferencias
    path('newsletter/', newsletter_preferences, name='newsletter_preferences'),
    path('newsletter/toggle/', toggle_newsletter_ajax, name='toggle_newsletter_ajax'),
    path('perfil/', profile_preferences, name='profile_preferences'),
]
