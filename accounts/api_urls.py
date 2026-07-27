from django.urls import path
from . import api_views
urlpatterns = [
    path('auth/register/', api_views.RegisterView.as_view(), name='register'),
    path('auth/profile/', api_views.UserProfileView.as_view(), name='profile'),
]
