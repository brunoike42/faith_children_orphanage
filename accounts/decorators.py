from functools import wraps
from django.shortcuts import render


def _is_staff_user(user):
    """A single, consistent definition of 'can use the custom admin dashboard'."""
    if not user.is_authenticated:
        return False
    return bool(user.is_staff or user.is_superuser or getattr(user, 'role', None) in ('admin', 'manager'))


def _is_admin_user(user):
    if not user.is_authenticated:
        return False
    return bool(user.is_superuser or getattr(user, 'role', None) == 'admin')


def staff_required(func):
    """Allows admins and managers (editors) into the custom dashboard."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not _is_staff_user(request.user):
            return render(request, 'accounts/access_denied.html', status=403)
        return func(request, *args, **kwargs)
    return wrapper


def admin_required(func):
    """Restricted to admins only (e.g. user management)."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not _is_admin_user(request.user):
            return render(request, 'accounts/access_denied.html', status=403)
        return func(request, *args, **kwargs)
    return wrapper


# Backwards-compatible alias used by earlier code.
editor_required = staff_required
