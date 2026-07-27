from django.shortcuts import render, get_object_or_404
from .models import Event

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

def event_form(request, pk=None):
    """Form for creating/editing events - admin only"""
    if not request.user.is_staff:
        return render(request, 'accounts/access_denied.html', status=403)
    
    event = None
    if pk:
        event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        # Handle form submission
        pass
    
    context = {
        'event': event,
    }
    return render(request, 'events/event_form.html', context)
