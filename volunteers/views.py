from django.core.mail import mail_admins
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import connection, OperationalError
from django.db.models import Q

from .forms import VolunteerOpportunityForm
from .models import Volunteer, VolunteerOpportunity, Child


def volunteers_tables_exist():
    try:
        return 'volunteers_child' in connection.introspection.table_names() and \
               'volunteers_volunteeropportunity' in connection.introspection.table_names()
    except OperationalError:
        return False


def seed_default_content():
    """Populate the site with demo content when the database is empty."""
    if not volunteers_tables_exist():
        return

    if not Child.objects.filter(is_active=True).exists():
        Child.objects.create(
            name='Amina',
            age=10,
            gender='female',
            quote='Every child deserves a safe home and a chance to learn.',
            description='Amina loves reading, drawing, and helping younger children feel welcome.',
            image='hero/girl_smiles.jfif',
            is_active=True,
            order=1,
        )
        Child.objects.create(
            name='Moses',
            age=12,
            gender='male',
            quote='A little care can change a whole future.',
            description='Moses enjoys football and dreams of becoming a teacher one day.',
            image='hero/boy_smiles.jfif',
            is_active=True,
            order=2,
        )
        Child.objects.create(
            name='Sarah',
            age=9,
            gender='female',
            quote='Kindness can turn hardship into hope.',
            description='Sarah is full of energy and loves music, storytelling, and community activities.',
            image='hero/girl_smiles_TBRYavy.jfif',
            is_active=True,
            order=3,
        )

    if not VolunteerOpportunity.objects.filter(is_active=True).exists():
        VolunteerOpportunity.objects.create(
            title='Community Outreach Volunteer',
            slug='community-outreach-volunteer',
            location='Jinja, Uganda',
            description='Support our outreach programs by visiting families, helping with distributions, and encouraging children and caregivers.',
            requirements='Friendly, dependable, and willing to spend a few hours each week with the community.',
            perks='Hands-on experience, guidance from our staff, and the joy of making a direct difference.',
            image='hero/boy_smiles.jfif',
            is_active=True,
            order=1,
        )
        VolunteerOpportunity.objects.create(
            title='Education Support Volunteer',
            slug='education-support-volunteer',
            location='Kampala, Uganda',
            description='Help children with homework, reading clubs, and learning activities that build confidence.',
            requirements='Good communication skills and a heart for mentoring young learners.',
            perks='Meaningful mentorship, practical teaching experience, and community impact.',
            image='hero/girl_smiles.jfif',
            is_active=True,
            order=2,
        )


def child_list(request):
    seed_default_content()
    children = []
    database_ready = volunteers_tables_exist()

    selected_age = request.GET.get('age_group', 'all')
    selected_gender = request.GET.get('gender', 'all')
    search_query = request.GET.get('search', '').strip()

    if database_ready:
        children = Child.objects.filter(is_active=True)

        if selected_gender != 'all':
            children = children.filter(gender=selected_gender)

        if selected_age != 'all':
            if selected_age == '0-5':
                children = children.filter(age__lte=5)
            elif selected_age == '6-8':
                children = children.filter(age__gte=6, age__lte=8)
            elif selected_age == '9-12':
                children = children.filter(age__gte=9, age__lte=12)
            elif selected_age == '13+':
                children = children.filter(age__gte=13)

        if search_query:
            children = children.filter(
                Q(name__icontains=search_query) |
                Q(quote__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        children = children.order_by('-order', 'name')

    context = {
        'children': children,
        'database_ready': database_ready,
        'selected_age': selected_age,
        'selected_gender': selected_gender,
        'search_query': search_query,
    }
    return render(request, 'volunteers/child_list.html', context)


def volunteer_list(request):
    """Display list of volunteer opportunities"""
    seed_default_content()
    opportunities = []
    database_ready = volunteers_tables_exist()
    if database_ready:
        opportunities = VolunteerOpportunity.objects.filter(is_active=True).order_by('-order', '-created_at')

        category = request.GET.get('category')
        if category:
            opportunities = opportunities.filter(title__icontains=category)
    else:
        category = None

    context = {
        'opportunities': opportunities,
        'database_ready': database_ready,
    }
    return render(request, 'volunteers/opportunity_list.html', context)


def volunteer_detail(request, pk):
    """Display details of a volunteer opportunity"""
    opportunity = get_object_or_404(VolunteerOpportunity, pk=pk, is_active=True)
    context = {
        'opportunity': opportunity,
    }
    return render(request, 'volunteers/opportunity_detail.html', context)


def apply_volunteer(request, pk):
    """Form for applying as a volunteer"""
    opportunity = get_object_or_404(VolunteerOpportunity, pk=pk, is_active=True)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        skills = request.POST.get('skills')
        availability = request.POST.get('availability')
        message = request.POST.get('message')

        if full_name and email:
            Volunteer.objects.create(
                opportunity=opportunity,
                full_name=full_name,
                email=email,
                phone=phone,
                skills=skills,
                availability=availability,
                message=message,
                status='pending'
            )
            mail_admins(
                subject=f'New volunteer application from {full_name}',
                message=(
                    f'A new volunteer application was submitted for "{opportunity.title}".\n\n'
                    f'Name: {full_name}\n'
                    f'Email: {email}\n'
                    f'Phone: {phone or "N/A"}\n'
                    f'Skills: {skills or "N/A"}\n'
                    f'Availability: {availability or "N/A"}\n'
                    f'Message: {message or "N/A"}\n'
                ),
            )
            messages.success(request, 'Your application has been submitted successfully.')
            return redirect('opportunity_list')

    context = {
        'opportunity': opportunity,
    }
    return render(request, 'volunteers/apply.html', context)


def volunteer_form(request, pk=None):
    """Form for creating/editing volunteer opportunities - admin only"""
    if not request.user.is_staff:
        return render(request, 'accounts/access_denied.html', status=403)

    opportunity = None
    if pk:
        opportunity = get_object_or_404(VolunteerOpportunity, pk=pk)

    if request.method == 'POST':
        form = VolunteerOpportunityForm(request.POST, request.FILES, instance=opportunity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Volunteer opportunity has been saved successfully.')
            return redirect('opportunity_list')
    else:
        form = VolunteerOpportunityForm(instance=opportunity)

    context = {
        'opportunity': opportunity,
        'title': 'Create Volunteer Opportunity' if opportunity is None else f'Edit: {opportunity.title}',
        'form': form,
    }
    return render(request, 'volunteers/opportunity_form.html', context)


def manage_opportunities(request):
    if not request.user.is_staff:
        return render(request, 'accounts/access_denied.html', status=403)

    opportunities = VolunteerOpportunity.objects.order_by('-is_active', '-order', '-created_at')
    return render(request, 'volunteers/manage_opportunities.html', {'opportunities': opportunities})


def manage_applications(request):
    if not request.user.is_staff:
        return render(request, 'accounts/access_denied.html', status=403)

    applications = Volunteer.objects.select_related('opportunity').order_by('-created_at')
    return render(request, 'volunteers/manage_applications.html', {'applications': applications})


def update_application_status(request, pk):
    if not request.user.is_staff:
        return render(request, 'accounts/access_denied.html', status=403)

    application = get_object_or_404(Volunteer, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Volunteer.STATUS_CHOICES):
            application.status = status
            application.save()
            messages.success(request, 'Application status updated.')
    return redirect('manage_applications')
