from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:pk>/', views.event_detail, name='event_detail'),

    # Custom admin dashboard
    path('manage/', views.manage_events, name='manage_events'),
    path('manage/add/', views.event_form, name='add_event'),
    path('manage/<int:pk>/edit/', views.event_form, name='edit_event'),
    path('manage/<int:pk>/delete/', views.delete_event, name='delete_event'),
]
