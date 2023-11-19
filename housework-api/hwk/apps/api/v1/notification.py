from typing import Dict, Any, List

from django.utils import timezone
from ninja import Router, Body
from ninja.errors import HttpError

from hwk.apps.api.v1.schema import NotificationSchema
from hwk.apps.notifications.models import SubscriptionChannelType, SubscriptionChannel, Notification

notification_router = Router(tags=["Notifications"])


@notification_router.get("unread", response=List[NotificationSchema])
def get_unread(request):
    return Notification.objects.filter(recipient=request.user, date_read=None)


@notification_router.post("subscribe", response=int)
def subscribe(request, enabled: bool = Body(...), name: str = Body(...), channel_type: SubscriptionChannelType = Body(...), config: Dict[str, Any] = Body(...)):
    sub, created = SubscriptionChannel.objects.update_or_create(
        name=name,
        channel_type=channel_type,
        defaults={'config': config, 'recipient': request.user, 'enabled': enabled}
    )
    return sub.id


@notification_router.post("all/read", response=int)
def mark_all_read(request):
    updated_count = Notification.objects.filter(recipient=request.user).update(date_read=timezone.now())
    return updated_count


@notification_router.post("{notification_id}/read", response=str)
def mark_read(request, notification_id: int):
    try:
        notifi = Notification.objects.get(id=notification_id, recipient=request.user)
    except Notification.DoesNotExist:
        raise HttpError(404, "Notification does not exist")
    notifi.date_read = timezone.now()
    notifi.save()
    return notifi.url

