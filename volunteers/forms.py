from django import forms

from .models import VolunteerOpportunity, Child


class VolunteerOpportunityForm(forms.ModelForm):
    class Meta:
        model = VolunteerOpportunity
        fields = [
            'title',
            'slug',
            'location',
            'description',
            'requirements',
            'perks',
            'image',
            'is_active',
            'order',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
            'perks': forms.Textarea(attrs={'rows': 3}),
        }

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = [
            'name', 'age', 'gender', 'quote', 'description', 'image',
            'is_active', 'order',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
