from django.contrib import admin
from .models import Child, VolunteerOpportunity, Volunteer

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'is_active', 'order')
    list_editable = ('age', 'gender', 'is_active', 'order')
    list_filter = ('gender', 'is_active')
    search_fields = ('name', 'quote', 'description')
    ordering = ('-order', 'name')
    fieldsets = (
        (None, {
            'fields': ('name', 'age', 'gender', 'image', 'quote', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(VolunteerOpportunity)
class VolunteerOpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'location', 'description')
    list_filter = ('is_active',)
    ordering = ('-order', '-created_at')


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'opportunity', 'status', 'created_at')
    list_filter = ('status', 'opportunity')
    search_fields = ('full_name', 'email', 'skills', 'message')
    raw_id_fields = ('opportunity',)
