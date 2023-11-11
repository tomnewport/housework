from typing import Literal, List, Optional
from uuid import UUID

from django.db import transaction
from ninja import Schema, Router, ModelSchema
from django.contrib.auth import get_user_model

from hwk.apps.api.v1.job import job_router
from hwk.apps.api.v1.schema import UserSchema
from hwk.apps.teams.models import Team, Membership, HolidayPolicy


class TeamCreateSchema(Schema):
    name: str
    policy_when_on_holiday: HolidayPolicy
    policy_max_team_diff: int
    policy_max_job_diff: int
    policy_team_credit_weight: int
    policy_job_credit_weight: int
    policy_random_weight: int


class MembershipSchema(ModelSchema):
    user: UserSchema

    class Config:
        model = Membership
        model_fields = "__all__"


class TeamResponse(ModelSchema):
    memberships: List[MembershipSchema]

    class Config:
        model = Team
        model_fields = '__all__'


class TeamUpdateSchema(Schema):
    name: Optional[str] = None
    policy_when_on_holiday: Optional[HolidayPolicy]
    policy_max_team_diff: Optional[int]
    policy_max_job_diff: Optional[int]
    policy_team_credit_weight: Optional[int]
    policy_job_credit_weight: Optional[int]
    policy_random_weight: Optional[int]


class ErrorResponse(Schema):
    success: Literal[False]
    message: str


class MemberManagementSchema(Schema):
    role: Membership.RoleChoices


class MembershipResponseSchema(ModelSchema):
    class Config:
        model = Membership
        model_fields = ['id']


team_router = Router(tags=["Team"])
team_router.add_router("/", job_router)


@team_router.post("/", response={403: ErrorResponse, 201: TeamResponse})
def create_team(request, team_data: TeamCreateSchema):
    user = request.user

    if (not user.is_superuser) and (Membership.objects.filter(user=user, role=Membership.RoleChoices.Admin).count() >= 10):
        return 403, {"success": False, "message": "Your account is limited to 10 teams"}

    team = Team.objects.create(**team_data.dict())

    # Create Membership for this user as Admin
    Membership.objects.create(user=user, team=team, role=Membership.RoleChoices.Admin)

    return 201, team


@team_router.get("/", response=List[TeamResponse])
def get_teams(request):
    user = request.user

    if user.is_superuser:
        # If the user is a superuser, fetch all teams
        teams = Team.objects.all()
    else:
        # If not a superuser, fetch teams where the user has membership
        teams = Team.objects.filter(membership__user=user)

    return teams.prefetch_related('memberships__user')


@team_router.patch('/{team_id}/', response={200: TeamResponse, 403: str, 404: str})
def update_team(request, team_id: UUID, data: TeamUpdateSchema):
    user = request.user

    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return 404, "Team not found"

    # Check if the user is a superuser or an admin of the team
    is_admin = Membership.objects.filter(user=user, team=team, role=Membership.RoleChoices.Admin).exists()
    if user.is_superuser or is_admin:
        # Update the team with the provided data
        for field, value in data.dict().items():
            if value is not None:
                setattr(team, field, value)
        team.save()
        return 200, team
    else:
        return 403, 'You do not have permission to edit this team'


@team_router.post('/{team_id}/members/{username}', response={200: TeamResponse, 403: str, 404: str, 400: str})
def add_member(request, team_id: UUID, username: str, data: MemberManagementSchema):
    user = request.user
    try:
        print(team_id, Team.objects.last().id)
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return 404, "Team not found"

    # Check if the user is authorized
    is_admin = Membership.objects.filter(user=user, team=team, role=Membership.RoleChoices.Admin).exists()
    try:
        new_member_user = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist:
        return 404, "User not found"

    if not (user.is_superuser or is_admin):
        return 403, 'You do not have permission to add members to this team'

    if Membership.objects.filter(team=team, role=Membership.RoleChoices.Admin).exclude(user=new_member_user).count() == 0:
        return 400, "Team must have at least one admin"

    with transaction.atomic():
        existing = Membership.objects.filter(user=new_member_user, team=team)
        existing_count = existing.count()
        if existing_count > 1:
            return 400, "User already has multiple memberships"

        if existing_count == 1:
            modify = existing.first()
            modify.role = data.role
            modify.save()
        else:
            Membership.objects.create(user=new_member_user, team=team, role=data.role)

    return 200, team


@team_router.delete('/{team_id}/members/{username}', response={200: TeamResponse, 403: str, 404: str, 400: str})
def remove_member(request, team_id: UUID, username: str):
    user = request.user
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist:
        return 404, "Team not found"

    # Check if the user is authorized
    is_admin = Membership.objects.filter(user=user, team=team, role=Membership.RoleChoices.Admin).exists()
    try:
        new_member_user = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist:
        return 404, "User not found"

    if not (user.is_superuser or is_admin):
        return 403, 'You do not have permission to add members to this team'

    if Membership.objects.filter(team=team, role=Membership.RoleChoices.Admin).exclude(user=new_member_user).count() == 0:
        return 400, "Team must have at least one admin"

    Membership.objects.filter(user=new_member_user, team=team).delete()

    return 200, team
