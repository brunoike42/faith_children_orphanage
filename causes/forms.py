from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit

from .models import Cause, Category


class CauseForm(forms.ModelForm):
    class Meta:
        model = Cause
        fields = [
            'title', 'slug', 'category', 'description', 'image',
            'goal_amount', 'raised_amount', 'is_active', 'is_featured',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'slug': forms.TextInput(attrs={'placeholder': 'auto-generated-if-left-blank'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['category'].required = False
        self.fields['image'].required = False
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'title',
            'slug',
            'category',
            'description',
            'image',
            Row(
                Column('goal_amount', css_class='col-md-6'),
                Column('raised_amount', css_class='col-md-6'),
            ),
            Row(
                Column('is_active', css_class='col-md-6'),
                Column('is_featured', css_class='col-md-6'),
            ),
        )

    def clean_slug(self):
        from django.utils.text import slugify
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('title', ''))
        qs = Category.objects.none()  # placeholder, real uniqueness check below
        existing = Cause.objects.filter(slug=slug)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            slug = f"{slug}-{Cause.objects.count() + 1}"
        return slug


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_slug(self):
        from django.utils.text import slugify
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('name', ''))
        return slug
