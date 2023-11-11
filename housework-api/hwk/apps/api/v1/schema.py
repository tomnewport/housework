from typing import List

from ninja import ModelSchema

from hwk.apps.jobs.models import JobConfig, JobVariant
from hwk.apps.people.models import HwkUser


class UserSchema(ModelSchema):
    class Config:
        model = HwkUser
        model_fields = ["id", "username", "approved", "first_name", "last_name", "is_superuser", "date_joined"]


class JobConfigCreateSchema(ModelSchema):
    class Config:
        model = JobConfig
        model_exclude = ["id", "team"]


class JobConfigUpdateSchema(ModelSchema):
    class Config:
        model = JobConfig
        model_exclude = ["id"]
        model_fields_optional = '__all__'


class JobVariantSchema(ModelSchema):
    class Config:
        model = JobVariant
        model_fields = "__all__"


class JobVariantCreateSchema(ModelSchema):
    class Config:
        model = JobVariant
        model_exclude = ["id", "job_config"]


class JobConfigSchema(ModelSchema):
    variants: List[JobVariantSchema]

    class Config:
        model = JobConfig
        model_fields = "__all__"

