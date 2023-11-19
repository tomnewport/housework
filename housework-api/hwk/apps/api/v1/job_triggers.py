from typing import List
from uuid import UUID

from ninja import Router
from ninja.errors import HttpError

from hwk.apps.api.v1.auth import has_team_permission_or_superuser
from hwk.apps.api.v1.schema import (
    JobTriggerSchema,
    JobTriggerCreateSchema,
    JobTriggerUpdateSchema,
    JobScheduleRuleCreateSchema,
    JobScheduleRuleSchema,
    JobScheduleRuleUpdateSchema,
)
from hwk.apps.jobs.models import JobTrigger, JobConfig, JobScheduleRule
from hwk.apps.jobs.rules import get_function, validate_rule
from hwk.apps.teams.models import Membership

job_triggers_router = Router(tags=["Job Triggers"])


@job_triggers_router.get("/{team_id}/triggers/", response=List[JobTriggerSchema])
def get_triggers(request, team_id: UUID):
    team = has_team_permission_or_superuser(
        request.user,
        team_id,
        [Membership.RoleChoices.Admin, Membership.RoleChoices.Member],
    )

    return JobTrigger.objects.filter(from_config__team_id=team.id)


@job_triggers_router.post("/{team_id}/triggers/", response=JobTriggerSchema)
def create_trigger(request, team_id: UUID, data: JobTriggerCreateSchema):
    team = has_team_permission_or_superuser(
        request.user, team_id, [Membership.RoleChoices.Admin]
    )

    try:
        from_config = JobConfig.objects.get(id=data.from_config, team_id=team.id)
        create_config = JobConfig.objects.get(id=data.from_config, team_id=team.id)
    except JobConfig.DoesNotExist:
        raise HttpError(400, "Job config must exist on team")

    return JobTrigger.objects.create(
        **{
            **data.dict().items(),
            "from_config": from_config,
            "create_config": create_config,
        }
    )


@job_triggers_router.delete("/{team_id}/triggers/{trigger_id}", response=None)
def delete_trigger(request, team_id: UUID, trigger_id: int):
    team = has_team_permission_or_superuser(
        request.user, team_id, [Membership.RoleChoices.Admin]
    )

    try:
        trigger = JobTrigger.objects.get(id=trigger_id, from_config__team_id=team.id)
    except JobTrigger.DoesNotExist:
        raise HttpError(400, "Trigger does not exist on team")

    trigger.delete()


@job_triggers_router.patch(
    "/{team_id}/triggers/{trigger_id}", response=JobTriggerSchema
)
def update_trigger(
    request, team_id: UUID, trigger_id: int, data: JobTriggerUpdateSchema
):
    team = has_team_permission_or_superuser(
        request.user, team_id, [Membership.RoleChoices.Admin]
    )

    try:
        trigger = JobTrigger.objects.get(id=trigger_id, from_config__team_id=team.id)
    except JobTrigger.DoesNotExist:
        raise HttpError(400, "Trigger does not exist on team")

    if data.from_config:
        try:
            from_config = JobConfig.objects.get(id=data.from_config, team_id=team.id)
        except JobConfig.DoesNotExist:
            raise HttpError(400, "From config must exist on team")
        trigger.from_config = from_config

    if data.create_config:
        try:
            from_config = JobConfig.objects.get(id=data.create_config, team_id=team.id)
        except JobConfig.DoesNotExist:
            raise HttpError(400, "From config must exist on team")
        trigger.from_config = from_config

    for key, value in data.dict(exclude_unset=True).items():
        if key not in ["create_config", "from_config"]:
            setattr(trigger, key, value)
    trigger.save()

    return trigger


@job_triggers_router.post(
    "/{team_id}/triggers/{trigger_id}/rules", response=JobScheduleRuleSchema
)
def add_rule_to_trigger(
    request, team_id: UUID, trigger_id: int, data: JobScheduleRuleCreateSchema
):
    team = has_team_permission_or_superuser(
        request.user, team_id, [Membership.RoleChoices.Admin]
    )

    try:
        trigger = JobTrigger.objects.get(id=trigger_id, from_config__team_id=team.id)
    except JobTrigger.DoesNotExist:
        raise HttpError(400, "Trigger does not exist on team")

    rule = JobScheduleRule.objects.create(
        trigger=trigger,
        rule_type=data.rule_type,
        params=data.params,
    )
    valid, error = validate_rule(rule)

    if not valid:
        raise HttpError(400, error)

    rule.save()
    return rule


@job_triggers_router.patch(
    "/{team_id}/triggers/{trigger_id}/rules/{rule_id}/", response=JobScheduleRuleSchema
)
def update_rule(
    request,
    team_id: UUID,
    trigger_id: int,
    rule_id: int,
    data: JobScheduleRuleUpdateSchema,
):
    team = has_team_permission_or_superuser(
        request.user, team_id, [Membership.RoleChoices.Admin]
    )

    try:
        rule = JobScheduleRule.objects.get(
            id=rule_id, trigger_id=trigger_id, trigger__from_config__team_id=team.id
        )
    except JobScheduleRule.DoesNotExist:
        raise HttpError(400, "Trigger does not exist on team")

    rule.params = data.params
    valid, error = validate_rule(rule)

    if not valid:
        raise HttpError(400, error)

    rule.save()
    return rule


@job_triggers_router.delete(
    "/{team_id}/triggers/{trigger_id}/rules/{rule_id}/", response=None
)
def delete_rule(
    request,
    team_id: UUID,
    trigger_id: int,
    rule_id: int,
    data: JobScheduleRuleUpdateSchema,
):
    team = has_team_permission_or_superuser(
        request.user, team_id, [Membership.RoleChoices.Admin]
    )

    try:
        rule = JobScheduleRule.objects.get(
            id=rule_id, trigger_id=trigger_id, trigger__from_config__team_id=team.id
        )
    except JobScheduleRule.DoesNotExist:
        raise HttpError(400, "Trigger does not exist on team")

    rule.delete()
