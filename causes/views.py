from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages

from accounts.decorators import staff_required
from .models import Cause, Category
from .forms import CauseForm, CategoryForm


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


# ---------------------------------------------------------------------------
# Custom admin dashboard: cause management
# ---------------------------------------------------------------------------

@staff_required
def manage_causes(request):
    causes = Cause.objects.select_related('category').order_by('-created_at')
    return render(request, 'causes/manage_causes.html', {'causes': causes})


@staff_required
def cause_form(request, pk=None):
    """Form for creating/editing causes - staff only"""
    cause = None
    if pk:
        cause = get_object_or_404(Cause, pk=pk)

    if request.method == 'POST':
        form = CauseForm(request.POST, request.FILES, instance=cause)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.pk:
                obj.created_by = request.user
            obj.save()
            messages.success(request, f'Cause "{obj.title}" saved successfully!')
            return redirect('manage_causes')
    else:
        form = CauseForm(instance=cause)

    context = {
        'form': form,
        'cause': cause,
        'title': 'Edit Cause' if cause else 'Add New Cause',
    }
    return render(request, 'causes/cause_form.html', context)


@staff_required
def delete_cause(request, pk):
    cause = get_object_or_404(Cause, pk=pk)
    if request.method == 'POST':
        title = cause.title
        cause.delete()
        messages.success(request, f'Cause "{title}" deleted.')
        return redirect('manage_causes')
    return render(request, 'causes/cause_confirm_delete.html', {'cause': cause})


@staff_required
def manage_categories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('manage_categories')
    else:
        form = CategoryForm()

    context = {
        'form': form,
        'categories': Category.objects.all(),
    }
    return render(request, 'causes/manage_categories.html', context)


@staff_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
    return redirect('manage_categories')
