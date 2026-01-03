from django.contrib import admin
from .models import MissingChild, AbductorInformation, LocationUpdate, Lead, AlertSubscription, EmergencyContact

@admin.register(MissingChild)
class MissingChildAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'first_name', 'last_name', 'age', 'gender', 'status', 'last_seen_date', 'reported_date']
    list_filter = ['status', 'gender', 'is_abducted', 'last_seen_date']
    search_fields = ['first_name', 'last_name', 'case_number', 'last_seen_location']
    readonly_fields = ['case_number', 'reported_date', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not obj.case_number:
            # Generate case number
            import datetime
            obj.case_number = f"MC-{datetime.datetime.now().strftime('%Y%m%d')}-{MissingChild.objects.count() + 1:04d}"
        if not obj.reported_by:
            obj.reported_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(AbductorInformation)
class AbductorInformationAdmin(admin.ModelAdmin):
    list_display = ['child', 'created_at', 'updated_at']
    search_fields = ['child__first_name', 'child__last_name', 'vehicle_plate']

@admin.register(LocationUpdate)
class LocationUpdateAdmin(admin.ModelAdmin):
    list_display = ['child', 'location', 'sighting_time', 'verified', 'reported_at']
    list_filter = ['verified', 'sighting_time']
    search_fields = ['child__first_name', 'child__last_name', 'location']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['child', 'reporter_name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['child__first_name', 'child__last_name', 'reporter_name', 'reporter_email']

@admin.register(AlertSubscription)
class AlertSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'location', 'subscribed', 'verified', 'created_at']
    list_filter = ['subscribed', 'verified']
    search_fields = ['email', 'location']

@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'phone', 'region', 'order', 'active']
    list_filter = ['active', 'region']
    search_fields = ['name', 'organization']