import json

from celery import current_app, shared_task
from django.db import models
from django.utils import timezone
from pywebpush import webpush, WebPushException

from hwk.apps.people.models import HwkUser


class SubscriptionChannelType(models.TextChoices):
    BROWSER_PUSH = "BRW_PSH", "Browser push notification"


class SubscriptionChannel(models.Model):
    recipient = models.ForeignKey(HwkUser, on_delete=models.CASCADE, related_name="subscription_channels")
    name = models.CharField(max_length=128)
    channel_type = models.CharField(max_length=8, choices=SubscriptionChannelType.choices)
    config = models.JSONField()
    enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ('name', 'channel_type',)


def browser_push(channel: SubscriptionChannel, notification: 'Notification'):
    sub = channel.config
    try:
        webpush(sub,
            json.dumps({
                "url": notification.url,
                "title": notification.title,
                "body": notification.body,
                "id": notification.id,
            }),
            vapid_private_key=,
            vapid_claims={
                "sub": "mailto:webmaster@tdn.sh"
            }
        )
        return True
    except WebPushException as e:
        try:
            if e.response.body["code"] in [410, 401, 403, 404]:
                return False
        except Exception as e:
            return True
    except Exception as e:
        return True


@shared_task
def send_notification(id):
    Notification.objects.get(id=id).send()


class Notification(models.Model):
    recipient = models.ForeignKey(HwkUser, on_delete=models.CASCADE)
    url = models.TextField(max_length=128)
    title = models.CharField(max_length=256)
    body = models.TextField()
    date_read = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)

    def bg_send(self):
        send_notification.delay(self.id)

    def send(self):
        delete_channels = []
        for channel in self.recipient.subscription_channels.all():
            if channel.channel_type == SubscriptionChannelType.BROWSER_PUSH:
                if not browser_push(channel, self):
                    delete_channels.append(channel)
        for channel in delete_channels:
            channel.delete()
