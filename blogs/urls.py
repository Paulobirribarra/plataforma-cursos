# blogs/urls.py
from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Lista de posts públicos
    path('', views.blog_list, name='list'),
    path('categoria/<str:categoria>/', views.blog_by_category, name='category'),
    
    # Post individual
    path('post/<slug:slug>/', views.blog_detail, name='post_detail'),
    
    # API para página nosotros
    path('api/destacados/', views.posts_destacados_json, name='destacados_api'),
    
    # Gestión de blog (solo para administradores)
    path('admin/', views.blog_admin_list, name='admin_list'),
    path('admin/crear/', views.blog_create, name='create'),
    path('admin/editar/<int:id>/', views.blog_edit, name='edit'),
    path('admin/eliminar/<int:id>/', views.blog_delete, name='delete'),
    path('admin/previsualizar/<int:id>/', views.blog_preview, name='preview'),
]
