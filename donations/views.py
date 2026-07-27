from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from urllib.parse import urlencode

from .models import Donation, ContactSubmission
from .forms import DonationForm
from causes.models import Cause

def get_pesapal_redirect_url(request, donation):
    api_url = getattr(settings, 'PESAPAL_API_URL', 'https://www.pesapal.com/API/PostPesapalDirectOrderV4')
    callback_url = getattr(settings, 'PESAPAL_CALLBACK_URL', request.build_absolute_uri(reverse('pesapal_callback')))
    payload = {
        'amount': f'{donation.amount:.2f}',
        'description': donation.message or f'Donation {donation.pk}',
        'type': 'MERCHANT',
        'reference': str(donation.pk),
        'first_name': donation.name.split()[0] if donation.name else 'Donor',
        'last_name': donation.name.split()[-1] if donation.name else '',
        'email': donation.email or 'donor@example.com',
        'currency': 'USD',
        'callback_url': callback_url,
    }
    return f"{api_url}?{urlencode(payload)}"

def donation_list(request):
    causes = Cause.objects.filter(is_active=True)
    selected_cause_id = request.GET.get('cause')
    selected_cause = None
    if selected_cause_id:
        try:
            selected_cause = Cause.objects.get(pk=selected_cause_id, is_active=True)
        except Cause.DoesNotExist:
            selected_cause = None

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            if request.user.is_authenticated:
                donation.donor = request.user
            donation.is_confirmed = False
            donation.save()
            return redirect('donation_checkout', donation_id=donation.pk)
    else:
        initial = {'cause': selected_cause.id} if selected_cause else {}
        form = DonationForm(initial=initial)

    context = {
        'form': form,
        'causes': causes,
        'cause': selected_cause,
    }
    return render(request, 'donations/donate.html', context)

def checkout(request, donation_id):
    donation = get_object_or_404(Donation, pk=donation_id)
    if request.method == 'POST':
        redirect_url = get_pesapal_redirect_url(request, donation)
        return redirect(redirect_url)

    context = {
        'donation': donation,
    }
    return render(request, 'donations/checkout.html', context)

def pesapal_callback(request):
    reference = request.GET.get('reference') or request.POST.get('reference')
    if reference:
        try:
            donation = Donation.objects.get(pk=reference)
            donation.is_confirmed = True
            donation.save()
        except Donation.DoesNotExist:
            pass
    return redirect('donation_checkout_success')

def checkout_success(request):
    return render(request, 'donations/checkout_success.html')

def donation_detail(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    
    context = {
        'donation': donation,
    }
    return render(request, 'donations/donation_detail.html', context)

def contact_view(request):
    """Handle contact form submissions"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email and message:
            ContactSubmission.objects.create(
                name=name,
                email=email,
                message=message
            )
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact')
    
    return render(request, 'donations/contact.html')

def donate_cause(request, cause_id):
    """Donation page for a specific cause"""
    cause = get_object_or_404(Cause, pk=cause_id, is_active=True)
    causes = Cause.objects.filter(is_active=True)

    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            if request.user.is_authenticated:
                donation.donor = request.user
            donation.is_confirmed = False
            donation.save()
            return redirect('donation_checkout', donation_id=donation.pk)
    else:
        form = DonationForm(initial={'cause': cause.id})

    context = {
        'form': form,
        'causes': causes,
        'cause': cause,
    }
    return render(request, 'donations/donate.html', context)
