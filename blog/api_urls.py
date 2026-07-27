from django.urls import path
from . import api_views
urlpatterns = [
    path('blog/', api_views.BlogPostListCreateView.as_view(), name='blog-list'),
    path('blog/<int:pk>/', api_views.BlogPostDetailView.as_view(), name='blog-detail'),
]
