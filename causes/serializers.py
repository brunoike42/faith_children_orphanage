from rest_framework import serializers
from .models import Cause, Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
class CauseSerializer(serializers.ModelSerializer):
    progress_percent = serializers.ReadOnlyField()
    class Meta:
        model = Cause
        fields = '__all__'
