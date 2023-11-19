from typing import List
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from hwk.apps.api.v1.auth import has_team_permission_or_superuser
from hwk.apps.api.v1.job import job_router
from hwk.apps.api.v1.job_triggers import job_triggers_router
from hwk.apps.api.v1.job_variants import job_variants_router
from hwk.apps.api.v1.schema import (
    JobConfigSchema,
    JobConfigCreateSchema,
    JobConfigUpdateSchema,
)
from hwk.apps.jobs.models import JobConfig
from hwk.apps.teams.models import Membership

job_config_router = Router(tags=["Job Configs"])
job_config_router.add_router("/", job_variants_router)
job_config_router.add_router("/", job_triggers_router)


@job_config_router.post("/{team_id}/jobconfigs/", response=JobConfigSchema)
def create_jobconfig(request, team_id: UUID, payload: JobConfigCreateSchema):
    team = has_team_permission_or_superuser(
        request.user, team_id, roles=[Membership.RoleChoices.Admin]
    )

    job_config = JobConfig.objects.create(**payload.dict(), team=team)
    return job_config


@job_config_router.get("/{team_id}/jobconfigs/", response=List[JobConfigSchema])
@paginate
def list_jobconfigs(request, team_id: UUID):
    has_team_permission_or_superuser(
        request.user,
        team_id,
        [Membership.RoleChoices.Admin, Membership.RoleChoices.Member],
    )
    return JobConfig.objects.filter(team_id=team_id)


@job_config_router.get(
    "/{team_id}/jobconfigs/{jobconfig_id}/", response=JobConfigSchema
)
def get_jobconfig(request, team_id: UUID, jobconfig_id: int):
    has_team_permission_or_superuser(
        request.user,
        team_id,
        [Membership.RoleChoices.Admin, Membership.RoleChoices.Member],
    )
    job_config = JobConfig.objects.filter(id=jobconfig_id, team_id=team_id).first()
    if not job_config:
        raise HttpError(404, "JobConfig not found")
    return job_config


@job_config_router.patch(
    "/{team_id}/jobconfigs/{jobconfig_id}/", response=JobConfigSchema
)
def patch_jobconfig(
    request, team_id: UUID, jobconfig_id: UUID, data: JobConfigUpdateSchema
):
    team = has_team_permission_or_superuser(
        request.user, team_id, [Membership.RoleChoices.Admin]
    )

    job_config = JobConfig.objects.filter(id=jobconfig_id, team=team).first()
    if not job_config:
        raise HttpError(404, "JobConfig not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(job_config, key, value)
    job_config.save()
    return job_config


@job_config_router.delete("/{team_id}/jobconfigs/{jobconfig_id}/", response={204: None})
def delete_jobconfig(request, team_id: UUID, jobconfig_id: UUID):
    team = has_team_permission_or_superuser(
        request.user, team_id, [Membership.RoleChoices.Admin]
    )

    job_config = JobConfig.objects.filter(id=jobconfig_id, team=team).first()
    if not job_config:
        raise HttpError(404, "JobConfig not found")

    job_config.delete()
    return 204, None
