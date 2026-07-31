from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from accounts.decorators import staff_required
from .models import HeroImage
from .forms import HeroImageForm


@staff_required
def manage_hero(request):
    hero_images = HeroImage.objects.all().order_by('-is_active', 'title')
    return render(request, 'core/manage_hero.html', {'hero_images': hero_images})


@staff_required
def hero_form(request, pk=None):
    hero = None
    if pk:
        hero = get_object_or_404(HeroImage, pk=pk)

    if request.method == 'POST':
        form = HeroImageForm(request.POST, request.FILES, instance=hero)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Hero image "{obj.title}" saved successfully!')
            return redirect('manage_hero')
    else:
        form = HeroImageForm(instance=hero)

    context = {
        'form': form,
        'hero': hero,
        'title': 'Edit Hero Image' if hero else 'Add New Hero Image',
    }
    return render(request, 'core/hero_form.html', context)


@staff_required
def delete_hero(request, pk):
    hero = get_object_or_404(HeroImage, pk=pk)
    if request.method == 'POST':
        title = hero.title
        hero.delete()
        messages.success(request, f'Hero image "{title}" deleted.')
        return redirect('manage_hero')
    return render(request, 'core/hero_confirm_delete.html', {'hero': hero})
