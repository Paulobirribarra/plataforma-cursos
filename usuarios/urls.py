#plataforma-cursos/usuarios/urls.py
from django.urls import path
from .views import dashboard, CustomSignupView, my_courses

app_name = "usuarios"

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('register/', CustomSignupView.as_view(), name='register'),
    path('mis-cursos/', my_courses, name='my_courses'),
]
