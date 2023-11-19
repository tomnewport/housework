from typing import Optional, Tuple

from django.db import models
from django.utils import timezone

from hwk.apps.notifications.events import EventType
from hwk.apps.notifications.models import Notification
from hwk.apps.people.models import HwkUser
from hwk.apps.teams.models import Team, Membership


class JobLifecycle(models.TextChoices):
    SCHEDULED = "Scheduled", "Scheduled"
    OPEN = "Open", "Open"
    OVERDUE = "Overdue", "Overdue"
    COMPLETE = "Complete", "Complete"
    CANCELLED = "Cancelled", "Cancelled"


class JobConfig(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="job_configs")
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    default_credit = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=True)
    open_days = models.PositiveSmallIntegerField(blank=True, null=True)
    failed_days = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class JobVariant(models.Model):
    job_config = models.ForeignKey(
        JobConfig, on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(max_length=128)
    description = models.TextField()
    credit = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Job(models.Model):
    job_config = models.ForeignKey(
        JobConfig, on_delete=models.CASCADE, null=True, blank=True
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    default_credit = models.PositiveSmallIntegerField()
    description = models.TextField(null=True, blank=True)
    explanation = models.TextField(null=True, blank=True)
    is_priority = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=JobLifecycle.choices, default=JobLifecycle.SCHEDULED
    )
    assignee = models.ForeignKey(
        Membership, on_delete=models.CASCADE, related_name="assigned_jobs"
    )
    completed_by = models.ForeignKey(
        Membership,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="completed_jobs",
    )
    delay = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name or f"Job {self.name}"

    def grabbed_rate(self, credits: Optional[int] = None) -> int:
        base = credits or self.default_credit
        if self.status in {JobLifecycle.CANCELLED, JobLifecycle.COMPLETE}:
            return 0
        if not self.due_date:
            return base
        days_count = (timezone.now() - self.due_date).days
        rate_diff = base * days_count * self.team.policy_overdue_inflation

        return max(0, int(base + rate_diff))

    def as_notification(self, member: Membership) -> Tuple[EventType, Notification]:
        event_type = EventType.JOB_SCHEDULED
        if self.status == JobLifecycle.SCHEDULED:
            event_type = EventType.JOB_SCHEDULED
        elif self.status == JobLifecycle.OPEN:
            event_type = EventType.JOB_OPEN
        elif self.status == JobLifecycle.OVERDUE:
            event_type = EventType.JOB_OVERDUE
        elif self.status == JobLifecycle.COMPLETE:
            event_type = EventType.JOB_COMPLETE
        elif self.status == JobLifecycle.CANCELLED:
            event_type = EventType.JOB_CANCELLED
        url = f"/jobs/{self.id}/"
        body = f"{self.name} ({self.team.name})"

        if self.completed_by:
            if member.id == self.completed_by:
                title = f"Job {str(self.status).lower()} by you"
            else:
                title = f"Job {str(self.status).lower()} by {self.completed_by.user}"
        elif self.assignee:
            if member.id == self.assignee.id:
                title = f"Job is {str(self.status).lower()} for you"
            else:
                title = f"Job is {str(self.status).lower()} for {self.assignee.user}"
        else:
            title = f"Unassigned job is {str(self.status).lower()}"

        return event_type, Notification(
            recipient=member.user,
            url=url,
            title=title,
            body=body,
        )


class JobTriggerExistingPolicy(models.TextChoices):
    REPLACE = "REPLACE", "Remove and replace all non-closed jobs for the config."
    SKIP = "SKIP", "Do not create new jobs if a job already exists for the config."
    DUPLICATE = "DUPLICATE", "Create new jobs, regardless of existing jobs."


class JobTrigger(models.Model):
    from_config = models.ForeignKey(
        JobConfig, on_delete=models.CASCADE, related_name="trigger_from"
    )
    create_config = models.ForeignKey(
        JobConfig, on_delete=models.CASCADE, related_name="trigger_create"
    )
    existing_job = models.CharField(
        max_length=10,
        choices=JobTriggerExistingPolicy.choices,
        default=JobTriggerExistingPolicy.REPLACE,
    )

    lifecycle_scheduled = models.BooleanField(default=False)
    lifecycle_open = models.BooleanField(default=False)
    lifecycle_overdue = models.BooleanField(default=False)
    lifecycle_complete = models.BooleanField(default=False)
    lifecycle_cancelled = models.BooleanField(default=False)

    urgent = models.BooleanField(default=False)

    def __str__(self):
        return f"Trigger from {self.from_config} to create {self.create_config}"


class JobScheduleRule(models.Model):
    class RuleType(models.TextChoices):
        DAY_IN_WEEK = "DayInWeek", "Day in Week"
        DAYS_SINCE = "DaysSince", "Days Since"
        DAY_IN_YEAR = "DayInYear", "Day in Year"

    trigger = models.ForeignKey(
        JobTrigger, on_delete=models.CASCADE, related_name="rules"
    )
    rule_type = models.CharField(max_length=10, choices=RuleType.choices)
    params = models.JSONField()

    def __str__(self):
        return f"{self.rule_type} - {self.trigger}"


class Credit(models.Model):
    amount = models.PositiveSmallIntegerField()
    job = models.ForeignKey(to=Job, on_delete=models.CASCADE, related_name="credits")
    person = models.ForeignKey(to=Membership, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.person} got {self.amount} from {self.job} on {self.job.closed_date}"
        )
