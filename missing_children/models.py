from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
import uuid

class MissingChild(models.Model):
    STATUS_CHOICES = [
        ('missing', 'Missing'),
        ('found', 'Found'),
        ('located', 'Located but not recovered'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    height = models.CharField(max_length=20, blank=True)
    weight = models.CharField(max_length=20, blank=True)
    eye_color = models.CharField(max_length=50, blank=True)
    hair_color = models.CharField(max_length=50, blank=True)
    last_seen_date = models.DateTimeField()
    last_seen_location = models.CharField(max_length=255)
    last_seen_wearing = RichTextField(blank=True)
    distinctive_features = RichTextField(blank=True)
    photo = models.ImageField(upload_to='missing_children/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='missing')
    is_abducted = models.BooleanField(default=False)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_cases')
    reported_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reported_date']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.case_number}"

class AbductorInformation(models.Model):
    child = models.OneToOneField(MissingChild, on_delete=models.CASCADE, related_name='abductor')
    description = RichTextField()
    vehicle_description = models.CharField(max_length=255, blank=True)
    vehicle_plate = models.CharField(max_length=50, blank=True)
    last_seen_direction = models.CharField(max_length=255, blank=True)
    known_associates = RichTextField(blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LocationUpdate(models.Model):
    child = models.ForeignKey(MissingChild, on_delete=models.CASCADE, related_name='location_updates')
    location = models.CharField(max_length=255)
    sighting_time = models.DateTimeField()
    reported_by = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20, blank=True)
    description = RichTextField()
    verified = models.BooleanField(default=False)
    reported_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sighting_time']

class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('investigating', 'Investigating'),
        ('verified', 'Verified'),
        ('false', 'False Lead'),
    ]
    
    child = models.ForeignKey(MissingChild, on_delete=models.CASCADE, related_name='leads')
    reported_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    reporter_name = models.CharField(max_length=100)
    reporter_email = models.EmailField()
    reporter_phone = models.CharField(max_length=20)
    information = RichTextField()
    evidence_file = models.FileField(upload_to='leads/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

class AlertSubscription(models.Model):
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=100, blank=True)
    subscribed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verification_token = models.CharField(max_length=100, blank=True)
    verified = models.BooleanField(default=False)

class EmergencyContact(models.Model):
    name = models.CharField(max_length=100)
    organization = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    region = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        
class SMSSubscription(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True)
    verification_sent_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    radius_miles = models.IntegerField(default=10)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone_number} - {'Verified' if self.verified else 'Pending'}"