from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Appointment

@receiver(post_save, sender=Appointment)
def send_appointment_notification(sender, instance, created, **kwargs):
    if created:
        # New appointment created
        subject = 'New Appointment Scheduled'
        context = {'appointment': instance}
        
        # Email to client
        client_message = render_to_string('emails/appointment_created_client.html', context)
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [instance.client.email],
            html_message=client_message
        )
        
        # Email to therapist
        therapist_message = render_to_string('emails/appointment_created_therapist.html', context)
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [instance.therapist.email],
            html_message=therapist_message
        )
    elif instance.status == Appointment.Status.CANCELLED:
        # Appointment cancelled
        subject = 'Appointment Cancelled'
        context = {'appointment': instance}
        
        # Email to client
        client_message = render_to_string('emails/appointment_cancelled_client.html', context)
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [instance.client.email],
            html_message=client_message
        )
        
        # Email to therapist
        therapist_message = render_to_string('emails/appointment_cancelled_therapist.html', context)
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [instance.therapist.email],
            html_message=therapist_message
        )