from rest_framework import generics, permissions
from .models import BlogPost, BlogCategory
from .serializers import BlogPostSerializer, BlogCategorySerializer
class BlogPostListCreateView(generics.ListCreateAPIView):
    queryset = BlogPost.objects.filter(is_published=True)
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]
class BlogPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAdminUser]
