from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
import uuid
from .models import MissingChild, Lead, AlertSubscription, LocationUpdate, EmergencyContact
from .forms import MissingChildForm, LeadForm, AlertSubscriptionForm, LocationUpdateForm, SearchForm

def home(request):
    urgent_cases = MissingChild.objects.filter(
        status='missing', 
        is_abducted=True
    ).order_by('-reported_date')[:5]
    
    recent_cases = MissingChild.objects.filter(status='missing').order_by('-reported_date')[:10]
    
    context = {
        'urgent_cases': urgent_cases,
        'recent_cases': recent_cases,
    }
    return render(request, 'missing_children/home.html', context)

def case_list(request):
    form = SearchForm(request.GET)
    cases = MissingChild.objects.filter(status='missing').order_by('-reported_date')
    
    if form.is_valid():
        q = form.cleaned_data.get('q')
        age_min = form.cleaned_data.get('age_min')
        age_max = form.cleaned_data.get('age_max')
        gender = form.cleaned_data.get('gender')
        status = form.cleaned_data.get('status')
        location = form.cleaned_data.get('location')
        
        if q:
            cases = cases.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(case_number__icontains=q) |
                Q(last_seen_location__icontains=q) |
                Q(distinctive_features__icontains=q)
            )
        
        if age_min:
            cases = cases.filter(age__gte=age_min)
        if age_max:
            cases = cases.filter(age__lte=age_max)
        if gender:
            cases = cases.filter(gender=gender)
        if status:
            cases = cases.filter(status=status)
        if location:
            cases = cases.filter(last_seen_location__icontains=location)
    
    paginator = Paginator(cases, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'missing_children/case_list.html', context)

def case_detail(request, pk):
    child = get_object_or_404(MissingChild, pk=pk)
    location_updates = child.location_updates.filter(verified=True).order_by('-sighting_time')
    context = {
        'child': child,
        'location_updates': location_updates,
    }
    return render(request, 'missing_children/case_detail.html', context)

def report_missing_child(request):
    if request.method == 'POST':
        form = MissingChildForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.status = 'missing'
            child.reported_by = request.user if request.user.is_authenticated else None
            child.save()
            
            # Send alert to subscribers
            send_alert_to_subscribers(child)
            
            messages.success(request, 'Missing child report submitted successfully!')
            return redirect('case_detail', pk=child.pk)
    else:
        form = MissingChildForm()
    
    context = {'form': form}
    return render(request, 'missing_children/report_missing.html', context)

def submit_lead(request, child_id):
    child = get_object_or_404(MissingChild, pk=child_id)
    
    if request.method == 'POST':
        form = LeadForm(request.POST, request.FILES)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.child = child
            if request.user.is_authenticated:
                lead.reported_by = request.user
            lead.save()
            
            messages.success(request, 'Thank you for submitting a lead. Authorities have been notified.')
            return redirect('case_detail', pk=child_id)
    else:
        form = LeadForm()
    
    context = {
        'form': form,
        'child': child,
    }
    return render(request, 'missing_children/submit_lead.html', context)

def subscribe_alerts(request):
    if request.method == 'POST':
        form = AlertSubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.verification_token = str(uuid.uuid4())
            subscription.save()
            
            # Send verification email
            verification_url = request.build_absolute_uri(
                f'/verify-email/{subscription.verification_token}/'
            )
            send_mail(
                'Verify your email for Missing Child Alerts',
                f'Please click this link to verify your email: {verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [subscription.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Please check your email to verify your subscription.')
            return redirect('home')
    else:
        form = AlertSubscriptionForm()
    
    context = {'form': form}
    return render(request, 'missing_children/subscribe.html', context)

def verify_email(request, token):
    subscription = get_object_or_404(AlertSubscription, verification_token=token)
    subscription.verified = True
    subscription.save()
    
    messages.success(request, 'Your email has been verified. You will now receive alerts.')
    return redirect('home')

def submit_location_update(request, child_id):
    child = get_object_or_404(MissingChild, pk=child_id)
    
    if request.method == 'POST':
        form = LocationUpdateForm(request.POST)
        if form.is_valid():
            location_update = form.save(commit=False)
            location_update.child = child
            location_update.save()
            
            messages.success(request, 'Location update submitted. Thank you for your help.')
            return redirect('case_detail', pk=child_id)
    else:
        form = LocationUpdateForm()
    
    context = {
        'form': form,
        'child': child,
    }
    return render(request, 'missing_children/location_update.html', context)

def emergency_contacts(request):
    contacts = EmergencyContact.objects.filter(active=True).order_by('order', 'name')
    context = {'contacts': contacts}
    return render(request, 'missing_children/emergency_contacts.html', context)

def search_cases(request):
    form = SearchForm(request.GET)
    cases = MissingChild.objects.all().order_by('-reported_date')
    
    if form.is_valid():
        q = form.cleaned_data.get('q')
        age_min = form.cleaned_data.get('age_min')
        age_max = form.cleaned_data.get('age_max')
        gender = form.cleaned_data.get('gender')
        location = form.cleaned_data.get('location')
        
        if q:
            cases = cases.filter(
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(case_number__icontains=q) |
                Q(last_seen_location__icontains=q)
            )
        
        if age_min:
            cases = cases.filter(age__gte=age_min)
        if age_max:
            cases = cases.filter(age__lte=age_max)
        if gender:
            cases = cases.filter(gender=gender)
        if location:
            cases = cases.filter(last_seen_location__icontains=location)
    
    context = {
        'cases': cases,
        'form': form,
    }
    return render(request, 'missing_children/search.html', context)

def send_alert_to_subscribers(child):
    subscriptions = AlertSubscription.objects.filter(subscribed=True, verified=True)
    
    for subscription in subscriptions:
        send_mail(
            f'URGENT: Missing Child Alert - {child.first_name} {child.last_name}',
            f'''
            Missing Child Alert
            
            Name: {child.first_name} {child.last_name}
            Age: {child.age}
            Last Seen: {child.last_seen_location}
            Date: {child.last_seen_date}
            
            Description: {child.distinctive_features}
            
            If you have any information, please contact authorities immediately.
            
            View details: [Link to case details]
            ''',
            settings.DEFAULT_FROM_EMAIL,
            [subscription.email],
            fail_silently=True,
        )