from django.db import models
from django.utils import timezone

from hwk.apps.teams.models import Team, Membership


class JobLifecycle(models.TextChoices):
    SCHEDULED = 'Scheduled', 'Scheduled'
    OPEN = 'Open', 'Open'
    OVERDUE = 'Overdue', 'Overdue'
    COMPLETE = 'Complete', 'Complete'
    CANCELLED = 'Cancelled', 'Cancelled'


class JobConfig(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='job_configs')
    name = models.CharField(max_length=128)
    description = models.TextField()
    default_credit = models.PositiveSmallIntegerField()
    active = models.BooleanField(default=True)
    open_days = models.PositiveSmallIntegerField(blank=True, null=True)
    failed_days = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class JobVariant(models.Model):
    job_config = models.ForeignKey(JobConfig, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=128)
    description = models.TextField()
    credit = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Job(models.Model):
    job_config = models.ForeignKey(JobConfig, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=128)
    default_credit = models.PositiveSmallIntegerField()
    description = models.TextField(null=True, blank=True)
    is_priority = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(null=True, blank=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=JobLifecycle.choices,
        default=JobLifecycle.SCHEDULED
    )
    assignee = models.ForeignKey(Membership, on_delete=models.CASCADE)

    def __str__(self):
        return self.name or f"Job {self.name}"


class JobTrigger(models.Model):
    from_config = models.ForeignKey(JobConfig, on_delete=models.CASCADE, related_name='trigger_from')
    create_config = models.ForeignKey(JobConfig, on_delete=models.CASCADE, related_name='trigger_create')
    lifecycle = models.CharField(max_length=50, choices=JobLifecycle.choices)
    urgent = models.BooleanField(default=False)

    def __str__(self):
        return f"Trigger from {self.from_config} to create {self.create_config}"


class JobScheduleRule(models.Model):
    class RuleType(models.TextChoices):
        DAY_IN_WEEK = 'DayInWeek', 'Day in Week'
        DAYS_SINCE = 'DaysSince', 'Days Since'
        DAY_IN_YEAR = 'DayInYear', 'Day in Year'

    trigger = models.ForeignKey(JobTrigger, on_delete=models.CASCADE)
    rule_type = models.CharField(max_length=10, choices=RuleType.choices)
    params = models.JSONField()

    def __str__(self):
        return f"{self.rule_type} - {self.trigger}"


class Credit(models.Model):
    amount = models.PositiveSmallIntegerField()
    job = models.ForeignKey(to=Job, on_delete=models.CASCADE)
    person = models.ForeignKey(to=Membership, on_delete=models.CASCADE)
