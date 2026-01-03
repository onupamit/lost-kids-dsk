from django import forms
from .models import MissingChild, Lead, AlertSubscription, LocationUpdate
from django.contrib.auth.models import User

class MissingChildForm(forms.ModelForm):
    class Meta:
        model = MissingChild
        fields = [
            'first_name', 'last_name', 'age', 'gender', 'height', 'weight',
            'eye_color', 'hair_color', 'last_seen_date', 'last_seen_location',
            'last_seen_wearing', 'distinctive_features', 'photo', 'is_abducted'
        ]
        widgets = {
            'last_seen_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['reporter_name', 'reporter_email', 'reporter_phone', 'information', 'evidence_file']

class AlertSubscriptionForm(forms.ModelForm):
    class Meta:
        model = AlertSubscription
        fields = ['email', 'location']

class LocationUpdateForm(forms.ModelForm):
    class Meta:
        model = LocationUpdate
        fields = ['location', 'sighting_time', 'reported_by', 'contact_number', 'description']
        widgets = {
            'sighting_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    age_min = forms.IntegerField(required=False, min_value=0, max_value=18, label='Min Age')
    age_max = forms.IntegerField(required=False, min_value=0, max_value=18, label='Max Age')
    gender = forms.ChoiceField(required=False, choices=[('', 'All')] + MissingChild.GENDER_CHOICES)
    status = forms.ChoiceField(required=False, choices=[('', 'All')] + MissingChild.STATUS_CHOICES)
    location = forms.CharField(required=False, max_length=100)