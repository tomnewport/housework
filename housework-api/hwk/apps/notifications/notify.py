from hwk.apps.jobs.models import Job


"""
notifications appear in preferences:
"notifications": {
    "": ["Team", "Assignee"]
}
"""


def on_job_change(job: Job):
    """
    Called whenever a job status changes
    """
    for member in job.team.memberships.all():
        subjects = {"Team"}
        if job.assignee and job.assignee.id == member.id:
            subjects.add("Assignee")
        if job.completed_by and job.completed_by.id == member.id:
            subjects.add("CompletedBy")
        event_type, notification = job.as_notification(member)
        notification.save()
        notification.bg_send()
