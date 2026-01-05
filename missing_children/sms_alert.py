import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings
from .models import AlertSubscription, MissingChild

logger = logging.getLogger(__name__)

class SMSAlertSystem:
    def __init__(self):
        self.client = None
        if all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN]):
            try:
                self.client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
    
    def send_sms_alert(self, child, phone_numbers):
        """Send SMS alerts for missing child"""
        if not self.client:
            logger.warning("Twilio client not configured")
            return False
        
        message = self._format_sms_message(child)
        results = []
        
        for phone_number in phone_numbers:
            try:
                message = self.client.messages.create(
                    body=message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=phone_number
                )
                results.append({
                    'phone': phone_number,
                    'success': True,
                    'message_sid': message.sid
                })
                logger.info(f"SMS sent to {phone_number} for child {child.id}")
            except TwilioRestException as e:
                logger.error(f"Failed to send SMS to {phone_number}: {e}")
                results.append({
                    'phone': phone_number,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def send_verification_sms(self, phone_number):
        """Send verification code via SMS"""
        if not self.client:
            return False
        
        try:
            verification = self.client.verify \
                .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                .verifications \
                .create(to=phone_number, channel='sms')
            
            return verification.status == 'pending'
        except TwilioRestException as e:
            logger.error(f"Failed to send verification SMS: {e}")
            return False
    
    def verify_sms_code(self, phone_number, code):
        """Verify SMS code"""
        if not self.client:
            return False
        
        try:
            verification_check = self.client.verify \
                .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                .verification_checks \
                .create(to=phone_number, code=code)
            
            return verification_check.status == 'approved'
        except TwilioRestException as e:
            logger.error(f"Failed to verify SMS code: {e}")
            return False
    
    def _format_sms_message(self, child):
        """Format SMS message for missing child"""
        message = f"🚨 MISSING CHILD ALERT 🚨\n\n"
        message += f"Name: {child.first_name} {child.last_name}\n"
        message += f"Age: {child.age}\n"
        message += f"Missing since: {child.last_seen_date.strftime('%Y-%m-%d %H:%M')}\n"
        message += f"Last seen: {child.last_seen_location}\n"
        
        if child.is_abducted:
            message += "⚠️ SUSPECTED ABDUCTION ⚠️\n"
        
        message += f"\nIf seen, call 911 immediately.\n"
        message += f"Case #{child.case_number}\n"
        message += f"More info: [Your Website URL]/case/{child.id}"
        
        # Ensure message doesn't exceed SMS limit
        if len(message) > 1600:
            message = message[:1597] + "..."
        
        return message
    
    def send_location_update_sms(self, child, location_update, subscribers):
        """Send SMS for location updates"""
        if not self.client:
            return False
        
        message = f"📍 SIGHTING UPDATE 🚨\n\n"
        message += f"{child.first_name} {child.last_name}\n"
        message += f"Reported at: {location_update.sighting_time.strftime('%Y-%m-%d %H:%M')}\n"
        message += f"Location: {location_update.location}\n"
        message += f"Reported by: {location_update.reported_by}\n"
        message += f"\nIf in area, stay alert.\nCall 911 if sighted."
        
        results = []
        for subscriber in subscribers:
            if subscriber.phone_verified and subscriber.sms_alerts:
                try:
                    sms = self.client.messages.create(
                        body=message,
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=subscriber.phone_number
                    )
                    results.append({
                        'subscriber': subscriber.id,
                        'success': True,
                        'message_sid': sms.sid
                    })
                except TwilioRestException as e:
                    results.append({
                        'subscriber': subscriber.id,
                        'success': False,
                        'error': str(e)
                    })
        
        return results