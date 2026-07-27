from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('events/', views.event_list, name='event_list_alt'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:pk>/', views.event_detail, name='event_detail_alt'),
    path('create/', views.event_form, name='event_create'),
    path('<int:pk>/edit/', views.event_form, name='event_edit'),
]
