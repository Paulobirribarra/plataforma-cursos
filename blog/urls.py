from django.urls import path
from . import views

urlpatterns = [

    path('newpost/', views.newPost, name='new-post'),
    path('mypost/', views.myPost, name='my-post'),
    path('posts/', views.posts, name='posts'),

]