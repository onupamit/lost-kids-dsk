from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import MissingChild, SMSSubscription, AlertSubscription
from .sms_alert import SMSAlertSystem
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_missing_child_alerts(child_id):
    """Send alerts for new missing child case"""
    try:
        child = MissingChild.objects.get(id=child_id)
        
        # Send email alerts
        email_subscribers = AlertSubscription.objects.filter(
            subscribed=True, 
            verified=True,
            location__icontains=child.last_seen_location[:50]  # Simple location matching
        )
        
        for subscriber in email_subscribers:
            send_mail(
                f'URGENT: Missing Child Alert - {child.first_name} {child.last_name}',
                f'Missing child alert...',
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                fail_silently=False,
            )
        
        # Send SMS alerts
        sms_system = SMSAlertSystem()
        sms_subscribers = SMSSubscription.objects.filter(
            verified=True, 
            active=True
        )
        
        phone_numbers = [sub.phone_number for sub in sms_subscribers]
        sms_results = sms_system.send_sms_alert(child, phone_numbers)
        
        # Log results
        successful_sms = len([r for r in sms_results if r['success']])
        logger.info(f"Sent {successful_sms}/{len(sms_results)} SMS alerts for child {child_id}")
        
        return {
            'emails_sent': email_subscribers.count(),
            'sms_sent': successful_sms,
            'child_id': child_id
        }
        
    except MissingChild.DoesNotExist:
        logger.error(f"Child {child_id} not found")
        return {'error': 'Child not found'}

@shared_task
def send_daily_digest():
    """Send daily digest of missing children"""
    from datetime import datetime, timedelta
    
    yesterday = datetime.now() - timedelta(days=1)
    new_cases = MissingChild.objects.filter(
        reported_date__gte=yesterday,
        status='missing'
    )
    
    if new_cases.exists():
        message = "📋 Daily Missing Children Digest\n\n"
        for case in new_cases:
            message += f"• {case.first_name} {case.last_name}, {case.age}\n"
            message += f"  Missing from: {case.last_seen_location}\n"
            message += f"  Case #{case.case_number}\n\n"
        
        message += "Stay vigilant in your community.\nReport sightings to 911."
        
        # Send to SMS subscribers
        sms_system = SMSAlertSystem()
        subscribers = SMSSubscription.objects.filter(
            verified=True, 
            active=True,
            digest_frequency='daily'
        )
        
        for subscriber in subscribers:
            sms_system.send_sms_alert(message, [subscriber.phone_number])
    
    return {'digest_sent': new_cases.count()}