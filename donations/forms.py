from django import forms
from .models import Donation
from causes.models import Cause


class DonationForm(forms.ModelForm):
    frequency = forms.ChoiceField(
        choices=Donation.FREQUENCY_CHOICES,
        widget=forms.HiddenInput(),
        initial='once'
    )
    amount = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '$ 0.00',
            'id': 'customAmount'
        })
    )

    class Meta:
        model = Donation
        fields = ['name', 'email', 'frequency', 'amount', 'cause', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'cause': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Leave a message (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cause'].queryset = Cause.objects.filter(is_active=True)
        self.fields['cause'].required = False
        self.fields['message'].required = False
