from datetime import date
from typing import List, Union, Literal, Optional
from uuid import UUID

from django.db.models import Q
from ninja import Router, Query, Body, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from hwk.apps.api.auth import HeaderUserAuth
from hwk.apps.api.v1.schema import JobSchema, JobCreateFromConfigSchema, JobCreateSchema, JobDetailSchema, \
    JobConfigSchema, JobTriggerSchema
from hwk.apps.jobs.lifecycle import set_job_status, process_job
from hwk.apps.jobs.models import JobLifecycle, Job, JobConfig, Credit, JobVariant
from hwk.apps.jobs.rules import dry_run
from hwk.apps.jobs.lifecycle import process_triggers
from hwk.apps.teams.models import Membership, Team

job_router = Router(tags=["Jobs"], auth=HeaderUserAuth(require_approved=True))


@job_router.get("/jobs/{job_id}", response=JobDetailSchema)
def get_job(request, job_id: int):
    try:
        return Job.objects.get(id=job_id, team__memberships__user_id=request.user.id)
    except Job.DoesNotExist:
        raise HttpError(404, "Not found")


@job_router.get("/jobs/", response=List[JobSchema])
@paginate
def get_jobs(
    request,
    config_id: List[int] = Query([]),
    only_self: bool = Query([False]),
    team_id: List[UUID] = Query([]),
    status: List[JobLifecycle] = Query([]),
):
    jobs = Job.objects.all()
    if only_self:
        jobs = jobs.filter(assignee__user=request.user)
    if len(team_id):
        jobs = jobs.filter(team_id__in=team_id)
    if len(status):
        jobs = jobs.filter(status__in=status)
    if len(config_id):
        jobs = jobs.filter(config_id__in=config_id)

    jobs = jobs.filter(
        Q(assignee__user=request.user) | Q(team__memberships__user=request.user)
    ).distinct()

    return jobs


@job_router.post("/jobs/from/{config_id}", response=JobSchema)
def create_job_from_config(
    request,
    config_id: int,
    data: JobCreateFromConfigSchema,
    complete: bool = False,
    variant: Optional[int] = None,
):
    try:
        config = JobConfig.objects.get(
            id=config_id, team__memberships__user=request.user
        )
    except JobConfig.DoesNotExist:
        raise HttpError(404, "Config not found")

    try:
        membership = Membership.objects.get(id=data.assignee, team_id=config.team.id)
    except Membership.DoesNotExist:
        raise HttpError(404, "Assignee not found")

    variant_model = None
    if variant:
        try:
            variant_model = JobVariant.objects.get(id=variant, job_config=config)
        except JobVariant.DoesNotExist:
            raise HttpError(400, "Variant does not exist")

    new_job = Job(
        job_config=config,
        default_credit=config.default_credit,
        team=config.team,
        name=config.name,
        **{**data.dict(), "assignee": membership}
    )
    new_job.save()
    process_triggers(new_job)
    process_job(new_job)

    if complete:
        if not set_job_status(
            new_job, JobLifecycle.COMPLETE, membership, job_variant=variant_model
        ):
            raise HttpError(403, "Transition is not allowed")

    return new_job


@job_router.post("/jobs/", response=JobSchema)
def create_job(request, data: JobCreateSchema):
    team = Team.objects.get(id=data.team, memberships__user=request.user)
    assignee = team.memberships.get(id=data.assignee)

    new_job = Job(
        **{
            **data.dict(),
            "team": team,
            "assignee": assignee,
        }
    )
    new_job.save()
    process_triggers(new_job)
    process_job(new_job)

    return new_job


@job_router.post("/jobs/{job_id}/status/{status}", response=JobSchema)
def close_job(
    request,
    job_id: int,
    status: Union[Literal[JobLifecycle.COMPLETE], Literal[JobLifecycle.CANCELLED]],
    delay: int = Body(0),
    variant: Optional[int] = Body(None),
):
    # Check if a job exists
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        raise HttpError(404, "Job could not be found")

    # Check the completing user is in the right team
    try:
        membership = job.team.memberships.get(user=request.user)
    except Membership.DoesNotExist:
        raise HttpError(403, "Not allowed to edit this job")

    # If a variant is specified, check it is in the config.
    # If so, use it as the credit amount.
    variant_model = None
    if variant:
        try:
            variant_model = JobVariant.objects.get(id=variant, job_config=job.job_config)
        except JobVariant.DoesNotExist:
            raise HttpError(400, "Variant does not exist")

    # Apply delay to the job and set completer
    job.delay = delay

    # Try and transition - 403 if not
    if not set_job_status(job, status, membership, job_variant=variant_model):
        raise HttpError(403, "Transition is not allowed")

    return job


class JobDryRunSchema(Schema):
    created_job: JobConfigSchema
    proposed_date: date
    trigger: JobTriggerSchema


@job_router.get("/jobs/{job_id}/dry_run/{action}", response=List[JobDryRunSchema])
def dry_run_job(request, job_id: int, action: JobLifecycle, delay: int = 0) -> List[JobDryRunSchema]:
    return dry_run(Job.objects.get(id=job_id), delay, action.value)
