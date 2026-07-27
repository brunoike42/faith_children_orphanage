from django.urls import path
from . import api_views
urlpatterns = [
    path('volunteers/', api_views.VolunteerListCreateView.as_view(), name='volunteer-list'),
    path('volunteers/<int:pk>/', api_views.VolunteerDetailView.as_view(), name='volunteer-detail'),
]
