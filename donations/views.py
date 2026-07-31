from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from urllib.parse import urlencode

from accounts.decorators import staff_required
from .models import Donation, ContactSubmission
from .forms import DonationForm
from .pesapal import (
    PesapalError, get_access_token, get_or_register_ipn_id,
    submit_order_request, get_transaction_status,
)
from causes.models import Cause
from volunteers.models import Child

# Pesapal's payment_status_description values, mapped to what we store locally.
PESAPAL_COMPLETED_STATUSES = {"COMPLETED"}
PESAPAL_FAILED_STATUSES = {"FAILED", "INVALID"}


def _update_donation_from_status(donation, status_data):
    """Given a GetTransactionStatus() response, update and save the donation."""
    description = (status_data or {}).get("payment_status_description", "")
    donation.payment_status = description
    if description.upper() in PESAPAL_COMPLETED_STATUSES:
        donation.is_confirmed = True
    donation.save()
    return description

def donation_list(request):
    causes = Cause.objects.filter(is_active=True)
    selected_cause_id = request.GET.get('cause')
    selected_cause = None
    if selected_cause_id:
        try:
            selected_cause = Cause.objects.get(pk=selected_cause_id, is_active=True)
        except Cause.DoesNotExist:
            selected_cause = None

    sponsored_child = None
    child_id = request.GET.get('child')
    if child_id:
        sponsored_child = Child.objects.filter(pk=child_id, is_active=True).first()

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
        'sponsored_child': sponsored_child,
    }
    return render(request, 'donations/donate.html', context)

def checkout(request, donation_id):
    donation = get_object_or_404(Donation, pk=donation_id)
    if request.method == 'POST':
        callback_url = getattr(settings, 'PESAPAL_CALLBACK_URL', '') or \
            request.build_absolute_uri(reverse('pesapal_callback'))
        first_name = donation.name.split()[0] if donation.name else 'Donor'
        last_name = donation.name.split()[-1] if donation.name and len(donation.name.split()) > 1 else ''

        try:
            token = get_access_token()
            ipn_id = get_or_register_ipn_id(token, callback_url)
            # Merchant reference must be unique per attempt so retries don't collide.
            merchant_reference = f"{donation.pk}-{int(donation.created_at.timestamp())}"
            order = submit_order_request(
                token,
                merchant_reference=merchant_reference,
                amount=donation.amount,
                description=donation.message or f'Donation #{donation.pk}',
                callback_url=callback_url,
                ipn_id=ipn_id,
                email=donation.email,
                first_name=first_name,
                last_name=last_name,
            )
        except PesapalError as exc:
            messages.error(
                request,
                f"We couldn't start the payment with Pesapal right now ({exc}). "
                "Please try again in a moment, or contact us if this keeps happening."
            )
            return redirect('donation_checkout', donation_id=donation.pk)

        donation.order_tracking_id = order['order_tracking_id']
        donation.save()
        return redirect(order['redirect_url'])

    context = {
        'donation': donation,
    }
    return render(request, 'donations/checkout.html', context)


def pesapal_response(request):
    """
    Single endpoint used for BOTH:
      - the browser callback (Pesapal redirects the donor's browser here), and
      - the server-to-server IPN alert (Pesapal calls this directly).
    Distinguished by the OrderNotificationType parameter.
    """
    order_tracking_id = request.GET.get('OrderTrackingId') or request.POST.get('OrderTrackingId')
    merchant_reference = request.GET.get('OrderMerchantReference') or request.POST.get('OrderMerchantReference')
    notification_type = request.GET.get('OrderNotificationType') or request.POST.get('OrderNotificationType')

    description = None
    ok = False
    if order_tracking_id:
        try:
            token = get_access_token()
            status_data = get_transaction_status(token, order_tracking_id)
            donation = Donation.objects.filter(order_tracking_id=order_tracking_id).first()
            if donation:
                description = _update_donation_from_status(donation, status_data)
            ok = True
        except PesapalError:
            ok = False

    if notification_type in ('IPNCHANGE', 'RECURRING'):
        # Server-to-server call: Pesapal requires this exact JSON acknowledgement shape.
        return JsonResponse({
            'orderNotificationType': notification_type,
            'orderTrackingId': order_tracking_id,
            'orderMerchantReference': merchant_reference,
            'status': 200 if ok else 500,
        })

    # Browser-facing callback: show the donor a normal page, never JSON.
    if description and description.upper() in PESAPAL_COMPLETED_STATUSES:
        return redirect('donation_checkout_success')
    return redirect('donation_checkout_failed')


def checkout_success(request):
    return render(request, 'donations/checkout_success.html')


def checkout_failed(request):
    return render(request, 'donations/checkout_failed.html')

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


# ---------------------------------------------------------------------------
# Custom admin dashboard: donations & contact messages
# ---------------------------------------------------------------------------

@staff_required
def manage_donations(request):
    donations = Donation.objects.select_related('cause', 'donor').order_by('-created_at')
    return render(request, 'donations/manage_donations.html', {'donations': donations})


@staff_required
def manage_messages(request):
    contact_messages = ContactSubmission.objects.order_by('-created_at')
    return render(request, 'donations/manage_messages.html', {'contact_messages': contact_messages})


@staff_required
def mark_message_read(request, pk):
    submission = get_object_or_404(ContactSubmission, pk=pk)
    submission.is_read = True
    submission.save()
    messages.success(request, 'Marked as read.')
    return redirect('manage_messages')
