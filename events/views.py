from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from accounts.decorators import staff_required
from .models import Event
from .forms import EventForm


def event_list(request):
    events = Event.objects.filter(is_active=True).order_by('-start_date', '-start_time')

    context = {
        'events': events,
    }
    return render(request, 'events/event_list.html', context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    related_events = Event.objects.filter(
        is_active=True
    ).exclude(pk=pk).order_by('-start_date', '-start_time')[:3]

    context = {
        'event': event,
        'related_events': related_events,
    }
    return render(request, 'events/event_detail.html', context)


# ---------------------------------------------------------------------------
# Custom admin dashboard: event management
# ---------------------------------------------------------------------------

@staff_required
def manage_events(request):
    events = Event.objects.order_by('-start_date', '-start_time')
    return render(request, 'events/manage_events.html', {'events': events})


@staff_required
def event_form(request, pk=None):
    """Form for creating/editing events - staff only"""
    event = None
    if pk:
        event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            obj = form.save()
            messages.success(request, f'Event "{obj.title}" saved successfully!')
            return redirect('manage_events')
    else:
        form = EventForm(instance=event)

    context = {
        'form': form,
        'event': event,
        'title': 'Edit Event' if event else 'Add New Event',
    }
    return render(request, 'events/event_form.html', context)


@staff_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'Event "{title}" deleted.')
        return redirect('manage_events')
    return render(request, 'events/event_confirm_delete.html', {'event': event})
