from django.contrib import admin
from .models import Category, Cause

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Cause)
class CauseAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal_amount', 'raised_amount', 'is_active', 'is_featured']
    list_editable = ['is_active', 'is_featured']
    prepopulated_fields = {'slug': ('title',)}
    
    