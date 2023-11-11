from datetime import timedelta, datetime

from django.utils import timezone

from hwk.apps.jobs.models import Job, JobLifecycle, JobTrigger
from hwk.apps.jobs.triggers import process_triggers


def get_lifecycle_for_job(job: Job):
    current_status = job.status

    if current_status == JobLifecycle.COMPLETE:
        return current_status

    if current_status == JobLifecycle.CANCELLED:
        return current_status

    if not job.due_date:
        return current_status

    open_time = job.due_date - timedelta(days=(job.job_config.open_days or 3650))
    failed_time = job.due_date + timedelta(days=(job.job_config.failed_days or 3650))

    current_time = datetime.now()

    if current_time > failed_time:
        return JobLifecycle.CANCELLED

    if current_time > job.due_date:
        return JobLifecycle.OVERDUE

    if current_time < open_time:
        return JobLifecycle.OPEN

    return current_status

def set_job_status(job: Job, desired_status: JobLifecycle):
    job.status = desired_status
    if desired_status in [JobLifecycle.COMPLETE, JobLifecycle.CANCELLED]:
        job.closed_date = timezone.now()
    process_triggers(job)
    job.save()


def process_jobs():
    open_jobs = Job.objects.filter(status_in=[JobLifecycle.OPEN, JobLifecycle.OVERDUE, JobLifecycle.SCHEDULED])

    for job in open_jobs:
        current_status = job.status
        desired_status = get_lifecycle_for_job(job)

        if current_status != desired_status:
            set_job_status(job, desired_status)
