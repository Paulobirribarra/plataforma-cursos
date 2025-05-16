#plataforma-cursos\plataforma_cursos\urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from cursos.views import course_list  # Importa la vista directamente
from cursos import views 

urlpatterns = [
    path('', course_list, name='home'),  # Página principal que usa course_list
    path('accounts/', include('allauth.urls')),  # URLs de django-allauth
    path('cursos/', include('cursos.urls')),  # Prefijo para las URLs de cursos
    path('usuarios/', include('usuarios.urls')),
    path('admin/', admin.site.urls),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('contacto/', views.contacto, name='contacto')
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)