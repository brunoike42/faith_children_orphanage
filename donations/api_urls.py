from django.urls import path
from . import api_views
urlpatterns = [
    path('donations/', api_views.DonationListCreateView.as_view(), name='donation-list'),
    path('donations/<int:pk>/', api_views.DonationDetailView.as_view(), name='donation-detail'),
    path('contact/', api_views.ContactSubmissionListCreateView.as_view(), name='contact-list'),
    path('contact/<int:pk>/', api_views.ContactSubmissionDetailView.as_view(), name='contact-detail'),
]
