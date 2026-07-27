from django.urls import path
from . import views

urlpatterns = [
    path('', views.cause_list, name='cause_list'),
    path('<int:pk>/', views.cause_detail, name='cause_detail'),
    path('create/', views.cause_form, name='cause_create'),
    path('<int:pk>/edit/', views.cause_form, name='cause_edit'),
]
