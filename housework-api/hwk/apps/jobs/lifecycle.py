from datetime import timedelta, datetime
from typing import Optional

from django.utils import timezone

from hwk.apps.jobs.assigner import create_job_from_trigger
from hwk.apps.jobs.models import Job, JobLifecycle, Credit, JobVariant, JobTrigger
from hwk.apps.notifications.notify import on_job_change
from hwk.apps.teams.models import Membership


def get_lifecycle_for_job(job: Job):
    current_status = job.status

    if current_status == JobLifecycle.COMPLETE:
        return current_status

    if current_status == JobLifecycle.CANCELLED:
        return current_status

    if not job.due_date:
        return current_status

    if not job.job_config:
        return current_status

    open_time = job.due_date - timedelta(days=(job.job_config.open_days or 3650))
    failed_time = job.due_date + timedelta(days=(job.job_config.failed_days or 3650))

    current_time = timezone.now()

    if current_time > failed_time:
        return JobLifecycle.CANCELLED

    if current_time > job.due_date:
        return JobLifecycle.OVERDUE

    if current_time > open_time:
        return JobLifecycle.OPEN

    return current_status


permitted_transitions = [
    (JobLifecycle.SCHEDULED, JobLifecycle.OPEN),
    (JobLifecycle.SCHEDULED, JobLifecycle.OVERDUE),
    (JobLifecycle.SCHEDULED, JobLifecycle.COMPLETE),
    (JobLifecycle.SCHEDULED, JobLifecycle.CANCELLED),
    (JobLifecycle.OPEN, JobLifecycle.OVERDUE),
    (JobLifecycle.OPEN, JobLifecycle.COMPLETE),
    (JobLifecycle.OPEN, JobLifecycle.CANCELLED),
    (JobLifecycle.OVERDUE, JobLifecycle.COMPLETE),
    (JobLifecycle.OVERDUE, JobLifecycle.CANCELLED),
]


def set_job_status(
    job: Job,
    desired_status: JobLifecycle,
    membership: Optional[Membership] = None,
    job_variant: Optional[JobVariant] = None,
):
    if (job.status, desired_status) not in permitted_transitions:
        return False

    original_status = job.status

    job.status = desired_status
    if desired_status in [JobLifecycle.COMPLETE, JobLifecycle.CANCELLED]:
        job.closed_date = timezone.now()

    if desired_status == JobLifecycle.COMPLETE:
        job.completed_by = membership
        credit_amount = job.default_credit
        if job_variant:
            credit_amount = job_variant.credit

        # Assign different credit if job is swapped over
        if job.completed_by != job.assignee:
            credit_amount = job.grabbed_rate(credit_amount)

        # Apply credit to the right membership
        Credit(job=job, amount=credit_amount, person=membership).save()

    process_triggers(job)
    job.save()

    if original_status != desired_status:
        on_job_change(job)

    return True


def process_triggers(job: Job):
    filter_params = {
        "from_config": job.job_config,
        f"lifecycle_{job.status.lower()}": True,
    }
    triggers = JobTrigger.objects.filter(**filter_params)
    for trigger in triggers:
        new_job = create_job_from_trigger(job, trigger)
        original_status = new_job.status
        process_job(new_job)
        if original_status == new_job.status:
            # Only notify if the job is still scheduled
            on_job_change(new_job)


def process_job(job):
    current_status = job.status
    desired_status = get_lifecycle_for_job(job)

    if current_status != desired_status:
        set_job_status(job, desired_status)


def process_jobs():
    open_jobs = Job.objects.filter(
        status__in=[JobLifecycle.OPEN, JobLifecycle.OVERDUE, JobLifecycle.SCHEDULED]
    )

    for job in open_jobs:
        process_job(job)
