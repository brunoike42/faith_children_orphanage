from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from .models import CustomUser
from .decorators import staff_required, admin_required

from causes.models import Cause
from events.models import Event
from blog.models import BlogPost
from donations.models import Donation, ContactSubmission
from volunteers.models import Volunteer


@login_required(login_url='login')
def dashboard(request):
    """User dashboard based on their role"""
    user = request.user

    if user.role == 'admin':
        template = 'accounts/admin_dashboard.html'
        stats = {
            'total_causes': Cause.objects.filter(is_active=True).count(),
            'total_donations': Donation.objects.filter(is_confirmed=True).aggregate(
                total=Sum('amount'))['total'] or 0,
            'total_donors': Donation.objects.filter(is_confirmed=True).exclude(email='').values('email').distinct().count(),
            'total_volunteers': Volunteer.objects.count(),
            'pending_applications': Volunteer.objects.filter(status='pending').count(),
            'unread_messages': ContactSubmission.objects.filter(is_read=False).count(),
        }
        context = {
            'user': user,
            'stats': stats,
            'recent_donations': Donation.objects.select_related('cause').order_by('-created_at')[:5],
            'recent_applications': Volunteer.objects.select_related('opportunity').order_by('-created_at')[:5],
        }
    elif user.role == 'manager':
        template = 'accounts/editor_dashboard.html'
        context = {
            'user': user,
            'stats': {
                'my_posts': BlogPost.objects.filter(author=user).count(),
                'total_causes': Cause.objects.filter(is_active=True).count(),
                'upcoming_events': Event.objects.filter(is_active=True, start_date__gte=date.today()).count(),
            },
        }
    else:  # donor
        template = 'accounts/donor_dashboard.html'
        my_donations = Donation.objects.filter(donor=user).select_related('cause').order_by('-created_at')
        my_applications = Volunteer.objects.filter(user=user).select_related('opportunity').order_by('-created_at')
        context = {
            'user': user,
            'my_donations': my_donations,
            'my_applications': my_applications,
            'total_donated': my_donations.filter(is_confirmed=True).aggregate(total=Sum('amount'))['total'] or 0,
        }

    return render(request, template, context)


@login_required(login_url='login')
def profile(request):
    """User profile page"""
    user = request.user

    if request.method == 'POST':
        # Update profile
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    context = {
        'user': user,
    }
    return render(request, 'accounts/profile.html', context)


def register(request):
    """User registration page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('register')

        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='donor'  # Default role
        )

        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')

    return render(request, 'accounts/register.html')


def access_denied(request):
    """Access denied page"""
    return render(request, 'accounts/access_denied.html', status=403)


# ---------------------------------------------------------------------------
# Custom admin dashboard: user management (admin only)
# ---------------------------------------------------------------------------

@admin_required
def manage_users(request):
    users = CustomUser.objects.order_by('-date_joined')
    return render(request, 'accounts/manage_users.html', {'users': users})


@admin_required
def change_user_role(request, pk):
    target = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(CustomUser.ROLE_CHOICES):
            target.role = new_role
            target.save()
            messages.success(request, f"{target.username}'s role is now {target.get_role_display()}.")
    return redirect('manage_users')


@admin_required
def toggle_user_status(request, pk):
    target = get_object_or_404(CustomUser, pk=pk)
    if target == request.user:
        messages.error(request, "You can't deactivate your own account.")
        return redirect('manage_users')
    target.is_active = not target.is_active
    target.save()
    messages.success(request, f"{target.username} is now {'active' if target.is_active else 'inactive'}.")
    return redirect('manage_users')
