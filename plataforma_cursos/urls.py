# plataforma-cursos/plataforma_cursos/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.generic import RedirectView

# Personalizar títulos del admin para mayor seguridad
admin.site.site_header = "Sistema de Gestión Interno"
admin.site.site_title = "Gestión Interna"
admin.site.index_title = "Panel de Control - Acceso Restringido"

urlpatterns = [
    path("", views.home, name="home"),  # Nueva página principal
    path("nosotros/", views.nosotros, name="nosotros"),  # Página Quiénes Somos
    path("contacto/", views.contacto, name="contacto"),  # Página de Contacto
    path("accounts/", include("allauth.urls")),  # URLs de django-allauth
    path(
        "cursos/", include("cursos.urls", namespace="cursos")
    ),  # Prefijo para las URLs de cursos
    path("usuarios/", include("usuarios.urls", namespace="usuarios")),
    # URL secreta para admin (cambiar por algo más seguro en producción)
    path("sistema-gestion-admin-2025/", admin.site.urls),
    path("pagos/", include("pagos.urls")),
    path("membresias/", include("membresias.urls")),    path("carrito/", include("carrito.urls", namespace="carrito")),
    # Blog URLs
    path("blog/", include("blogs.urls", namespace="blog")),
    # Boletines URLs
    path("boletines/", include("boletines.urls", namespace="boletines")),
    # Redirección personalizada
    path(
        "accounts/confirm-email/",
        RedirectView.as_view(url="/accounts/email/", permanent=False),
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
