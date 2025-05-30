#cursos/urls.py
from django.urls import path
from . import views

app_name = 'cursos'

urlpatterns = [
    # Vistas públicas
    path('', views.course_list, name='course_list'),
    path('course/<int:pk>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/resource/<int:resource_id>/', views.access_resource, name='access_resource'),
    # Vistas de administración
    path('admin/courses/', views.course_list_admin, name='course_list_admin'),
    path('admin/course/create/', views.course_create_or_update, name='course_create_admin'),
    path('admin/course/<int:pk>/edit/', views.course_create_or_update, name='course_edit_admin'),
    path('admin/course/<int:pk>/delete/', views.course_delete, name='course_delete_admin'),
    path('admin/course/<int:course_pk>/resource/create/', views.course_resource_create, name='course_resource_create'),
]