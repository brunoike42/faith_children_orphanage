from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser

@login_required(login_url='login')
def dashboard(request):
    """User dashboard based on their role"""
    user = request.user
    
    if user.role == 'admin':
        template = 'accounts/admin_dashboard.html'
    elif user.role == 'manager':
        template = 'accounts/editor_dashboard.html'
    else:  # donor
        template = 'accounts/donor_dashboard.html'
    
    context = {
        'user': user,
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
