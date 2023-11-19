from typing import List
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError
from ninja.pagination import paginate

from hwk.apps.api.v1.auth import has_team_permission_or_superuser
from hwk.apps.api.v1.schema import JobVariantSchema, JobVariantCreateSchema
from hwk.apps.jobs.models import JobVariant, JobConfig
from hwk.apps.teams.models import Membership

job_variants_router = Router(tags=["Job Variants"])


@job_variants_router.get(
    "/{team_id}/jobconfigs/{job_config_id}/variants/", response=List[JobVariantSchema]
)
@paginate
def list_jobconfig_variants(request, team_id: UUID, job_config_id: int):
    team = has_team_permission_or_superuser(
        request.user,
        team_id,
        [Membership.RoleChoices.Admin, Membership.RoleChoices.Member],
    )
    return JobVariant.objects.filter(
        job_config_id=job_config_id, job_config__team_id=team.id
    )


@job_variants_router.get(
    "/{team_id}/jobconfigs/{job_config_id}/variants/{variant_id}/",
    response=JobVariantSchema,
)
def get_jobvariant(request, team_id: UUID, job_config_id: int, variant_id: int):
    team = has_team_permission_or_superuser(
        request.user,
        team_id,
        [Membership.RoleChoices.Admin, Membership.RoleChoices.Member],
    )
    job_variant = JobVariant.objects.filter(
        id=variant_id, job_config_id=job_config_id, job_config__team_id=team.id
    ).first()
    if not job_variant:
        raise HttpError(404, "JobVariant not found")
    return job_variant


@job_variants_router.delete(
    "/{team_id}/jobconfigs/{job_config_id}/variants/{variant_id}/", response=None
)
def delete_jobvariant(request, team_id: UUID, job_config_id: int, variant_id: int):
    team = has_team_permission_or_superuser(
        request.user,
        team_id,
        [Membership.RoleChoices.Admin, Membership.RoleChoices.Member],
    )
    JobVariant.objects.filter(
        id=variant_id, job_config_id=job_config_id, job_config__team_id=team.id
    ).delete()
    return 200, None


@job_variants_router.post(
    "/{team_id}/jobconfigs/{job_config_id}/variants/", response=JobVariantSchema
)
def create_jobconfig_variant(
    request, team_id: UUID, job_config_id: int, data: JobVariantCreateSchema
):
    team = has_team_permission_or_superuser(
        request.user,
        team_id,
        [Membership.RoleChoices.Admin, Membership.RoleChoices.Member],
    )
    try:
        JobConfig.objects.get(id=job_config_id, team_id=team.id)
    except JobConfig.DoesNotExist:
        raise HttpError(404, "Job config not found.")

    return JobVariant.objects.create(job_config_id=job_config_id, **data.dict())
