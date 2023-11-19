from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from hwk.apps.jobs.lifecycle import process_jobs
from hwk.apps.notifications.models import Notification


@shared_task
def housekeeping():
    process_jobs()
    # Delete old notifications
    Notification.objects.filter(date_read__lt=timezone.now() - timedelta(hours=12)).delete()
