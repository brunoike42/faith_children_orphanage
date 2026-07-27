from functools import wraps
from django.shortcuts import render

def admin_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            return render(request, 'accounts/access_denied.html', status=403)
        return func(request, *args, **kwargs)
    return wrapper

def editor_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ('admin', 'editor'):
            return render(request, 'accounts/access_denied.html', status=403)
        return func(request, *args, **kwargs)
    return wrapper
