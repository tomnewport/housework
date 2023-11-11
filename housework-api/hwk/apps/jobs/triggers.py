from hwk.apps.jobs.assigner import create_job_from_trigger
from hwk.apps.jobs.models import JobTrigger, Job


def process_triggers(job: Job):
    triggers = JobTrigger.objects.filter(from_config=job.job_config, lifecycle=job.status)
    for trigger in triggers:
        create_job_from_trigger(job, trigger)
