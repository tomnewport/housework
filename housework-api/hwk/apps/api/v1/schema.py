from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ninja import ModelSchema, Schema

from hwk.apps.jobs.models import (
    JobConfig,
    JobVariant,
    JobTrigger,
    JobScheduleRule,
    JobLifecycle,
    Job, Credit,
)
from hwk.apps.jobs.rules import validate_rule
from hwk.apps.notifications.models import Notification
from hwk.apps.people.models import HwkUser
from hwk.apps.teams.models import Membership, Team, Invitation


class UserSchema(ModelSchema):
    class Config:
        model = HwkUser
        model_fields = [
            "id",
            "username",
            "approved",
            "full_name",
            "short_name",
            "is_superuser",
            "date_joined",
        ]


class TeamSelfSchema(ModelSchema):
    class Config:
        model = Team
        model_fields = "__all__"


class MembershipSelfSchema(ModelSchema):
    team: TeamSelfSchema
    class Config:
        model = Membership
        model_fields = ["team", "role"]


class UserSelfSchema(ModelSchema):
    memberships: List[MembershipSelfSchema]
    is_set_up: bool
    has_usable_password: bool

    class Config:
        model = HwkUser
        model_fields = [
            "id",
            "username",
            "approved",
            "full_name",
            "short_name",
            "is_superuser",
            "date_joined",
            "preferences",
        ]


class JobConfigCreateSchema(ModelSchema):
    class Config:
        model = JobConfig
        model_exclude = ["id", "team"]


class JobConfigUpdateSchema(ModelSchema):
    class Config:
        model = JobConfig
        model_exclude = ["id"]
        model_fields_optional = "__all__"


class JobVariantSchema(ModelSchema):
    class Config:
        model = JobVariant
        model_fields = "__all__"


class JobVariantCreateSchema(ModelSchema):
    class Config:
        model = JobVariant
        model_exclude = ["id", "job_config"]


class JobScheduleRuleSchema(ModelSchema):
    summary: str

    class Config:
        model = JobScheduleRule
        model_fields = "__all__"

    @staticmethod
    def resolve_summary(obj):
        valid, message = validate_rule(obj)
        if valid:
            return message
        else:
            return f"[ERROR] {message}"


class JobScheduleRuleCreateSchema(ModelSchema):
    class Config:
        model = JobScheduleRule
        model_exclude = ["id", "trigger"]


class JobScheduleRuleUpdateSchema(ModelSchema):
    class Config:
        model = JobScheduleRule
        model_fields = ["params"]


class JobTriggerSchema(ModelSchema):
    rules: List[JobScheduleRuleSchema]

    class Config:
        model = JobTrigger
        model_fields = "__all__"

class JobConfigSchema(ModelSchema):
    variants: List[JobVariantSchema]
    trigger_from: List[JobTriggerSchema]
    trigger_create: List[JobTriggerSchema]

    class Config:
        model = JobConfig
        model_fields = "__all__"

class JobTriggerCreateSchema(ModelSchema):
    class Config:
        model = JobTrigger
        model_exclude = ["id"]


class JobTriggerUpdateSchema(Schema):
    from_config: Optional[int]
    create_config: Optional[int]
    urgent: Optional[bool]
    lifecycle_scheduled: Optional[bool]
    lifecycle_open: Optional[bool]
    lifecycle_overdue: Optional[bool]
    lifecycle_complete: Optional[bool]
    lifecycle_cancelled: Optional[bool]


class JobSchema(ModelSchema):
    grabbed_rate: int

    class Config:
        model = Job
        model_fields = "__all__"


class JobCreateFromConfigSchema(ModelSchema):
    class Config:
        model = Job
        model_fields = ["is_priority", "due_date", "assignee"]


class JobCreateSchema(Schema):
    team: UUID
    name: str
    default_credit: int
    description: Optional[str]
    is_priority: bool
    due_date: datetime
    assignee: int


class MembershipSchema(ModelSchema):
    user: UserSchema

    class Config:
        model = Membership
        model_fields = "__all__"


class TeamResponse(ModelSchema):
    memberships: List[MembershipSchema]

    class Config:
        model = Team
        model_fields = "__all__"


class CreditSchema(ModelSchema):

    person: MembershipSchema
    class Config:
        model = Credit
        model_fields = "__all__"


class JobDetailSchema(JobSchema):
    credits: List[CreditSchema]
    team: TeamSelfSchema
    job_config: Optional[JobConfigSchema]
    assignee: MembershipSchema
    completed_by: Optional[MembershipSchema]


class NotificationSchema(ModelSchema):
    class Config:
        model = Notification
        model_fields = "__all__"


class InvitationSchema(ModelSchema):
    issuer: UserSchema
    team: TeamResponse

    class Config:
        model = Invitation
        model_exclude = ["blocked"]
