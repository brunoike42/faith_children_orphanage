from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('create/', views.post_form, name='post_create'),
    path('<int:pk>/edit/', views.post_form, name='post_edit'),
]