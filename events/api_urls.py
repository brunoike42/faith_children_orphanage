from django.urls import path
from . import api_views
urlpatterns = [
    path('events/', api_views.EventListCreateView.as_view(), name='event-list'),
    path('events/<int:pk>/', api_views.EventDetailView.as_view(), name='event-detail'),
]
