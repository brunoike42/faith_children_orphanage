from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Cause, Category

def cause_list(request):
    causes = Cause.objects.filter(is_active=True).order_by('-created_at')
    categories = Category.objects.all()
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        causes = causes.filter(category_id=category_id)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        causes = causes.filter(Q(title__icontains=search) | Q(description__icontains=search))
    
    context = {
        'causes': causes,
        'categories': categories,
        'search': search,
    }
    return render(request, 'causes/cause_list.html', context)

def cause_detail(request, pk):
    cause = get_object_or_404(Cause, pk=pk, is_active=True)
    related_causes = Cause.objects.filter(
        is_active=True,
        category=cause.category
    ).exclude(pk=pk)[:3]
    
    context = {
        'cause': cause,
        'related_causes': related_causes,
    }
    return render(request, 'causes/cause_detail.html', context)

def cause_form(request, pk=None):
    """Form for creating/editing causes - admin only"""
    if not request.user.is_staff:
        return render(request, 'accounts/access_denied.html', status=403)
    
    cause = None
    if pk:
        cause = get_object_or_404(Cause, pk=pk)
    
    if request.method == 'POST':
        # Handle form submission
        pass
    
    context = {
        'cause': cause,
        'categories': Category.objects.all(),
    }
    return render(request, 'causes/cause_form.html', context)
