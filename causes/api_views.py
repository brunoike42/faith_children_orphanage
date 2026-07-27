from rest_framework import generics, permissions
from .models import Cause, Category
from .serializers import CauseSerializer, CategorySerializer
class CauseListCreateView(generics.ListCreateAPIView):
    queryset = Cause.objects.filter(is_active=True)
    serializer_class = CauseSerializer
    permission_classes = [permissions.AllowAny]
class CauseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cause.objects.all()
    serializer_class = CauseSerializer
    permission_classes = [permissions.IsAdminUser]
