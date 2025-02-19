# api/signals.py

from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Complaint

@receiver(pre_save, sender=Complaint)
def generate_complaint_number(sender, instance, **kwargs):
    if not instance.complaint_number:  # Only generate the ticket number if it's not set already
        last_ticket = Complaint.objects.order_by('-id').first()

        # Find the last ticket number and increment it for a new unique ticket number
        last_complaint_number = int(last_ticket.complaint_number) if last_ticket else 0
        new_complaint_number = last_complaint_number + 1
        new_complaint_number_str = str(new_complaint_number).zfill(6)  # Pad with zeros to ensure 6 digits

        # Check if the new_complaint_number is already used, and keep incrementing until it's unique
        while Complaint.objects.filter(complaint_number=new_complaint_number_str).exists():
            new_complaint_number += 1
            new_complaint_number_str = str(new_complaint_number).zfill(6)

        instance.complaint_number = new_complaint_number_str
