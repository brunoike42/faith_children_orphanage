from django import forms

from .models import HeroImage


class HeroImageForm(forms.ModelForm):
    class Meta:
        model = HeroImage
        fields = ['title', 'subtitle', 'image', 'is_active']
        widgets = {
            'subtitle': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subtitle'].required = False
