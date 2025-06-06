from django.urls import path
from . import views

app_name = 'boletines'

urlpatterns = [
    # URLs de administración (solo staff) - DEBEN IR PRIMERO para evitar conflictos con slug
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/crear/', views.AdminCrearView.as_view(), name='admin_crear'),
    path('admin/<slug:slug>/editar/', views.AdminEditarView.as_view(), name='admin_editar'),
    path('admin/<slug:slug>/eliminar/', views.AdminEliminarView.as_view(), name='admin_eliminar'),
    path('admin/<slug:slug>/enviar/', views.AdminEnviarView.as_view(), name='admin_enviar'),
    path('admin/<slug:slug>/preview/', views.AdminPreviewView.as_view(), name='admin_preview'),
    path('admin/<slug:slug>/duplicar/', views.AdminDuplicarView.as_view(), name='admin_duplicar'),
    path('admin/<slug:slug>/estadisticas/', views.AdminEstadisticasView.as_view(), name='admin_estadisticas'),
    
    # URLs de plantillas
    path('admin/plantillas/', views.AdminPlantillasView.as_view(), name='admin_plantillas'),
    path('admin/plantillas/crear/', views.AdminCrearPlantillaView.as_view(), name='admin_crear_plantilla'),
    path('admin/plantillas/<int:pk>/editar/', views.AdminEditarPlantillaView.as_view(), name='admin_editar_plantilla'),
    path('admin/plantillas/<int:pk>/eliminar/', views.AdminEliminarPlantillaView.as_view(), name='admin_eliminar_plantilla'),
    
    # APIs AJAX
    path('api/preview-template/', views.APIPreviewTemplateView.as_view(), name='api_preview_template'),
    path('api/destinatarios-count/', views.APIDestinatariosCountView.as_view(), name='api_destinatarios_count'),
    
    # URLs de tracking - DEBEN IR ANTES que el slug genérico
    path('tracking/<slug:slug>/abrir/', views.TrackingAbrirView.as_view(), name='tracking_abrir'),
    path('tracking/<slug:slug>/click/', views.TrackingClickView.as_view(), name='tracking_click'),
      # URLs públicas - EL SLUG GENÉRICO DEBE IR AL FINAL
    path('', views.BoletinListView.as_view(), name='lista'),
    path('suscribir/', views.SuscribirBoletinView.as_view(), name='suscribir'),
    path('<slug:slug>/', views.BoletinDetailView.as_view(), name='detalle'),
]
