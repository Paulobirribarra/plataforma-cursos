from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('admin/cursos/', views.course_list_admin, name='course_list_admin'),
    path('admin/cursos/crear/', views.course_create, name='course_create'),
    path('admin/cursos/<int:pk>/editar/', views.course_update, name='course_update'),
    path('admin/cursos/<int:pk>/eliminar/', views.course_delete, name='course_delete'),
    path('curso/<int:pk>/', views.course_detail, name='course_detail'),
]