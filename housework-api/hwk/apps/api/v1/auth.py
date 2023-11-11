from typing import List

from django.contrib.auth import authenticate, login, logout
from ninja import Router, Schema
from ninja.errors import HttpError

from hwk.apps.teams.models import Membership, Team

auth_router = Router(tags=["Authentication"])


class LoginSchema(Schema):
    username: str
    password: str


@auth_router.post('/session')
def login_user(request, data: LoginSchema):
    user = authenticate(request, username=data.username, password=data.password)
    if user is not None:
        login(request, user)
        return {"success": True, "message": "User successfully logged in."}
    else:
        return {"success": False, "message": "Invalid username or password."}


@auth_router.delete('/session')
def logout_user(request):
    logout(request)
    return {"success": True, "message": "User successfully logged out."}


def has_team_permission_or_superuser(user, team_id, roles: List[Membership.RoleChoices]) -> bool:
    if user.is_superuser:
        try:
            return Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise HttpError(404, "Team does not exist")

    membership = Membership.objects.filter(user=user, team_id=team_id).first()

    if membership.role not in roles:
        raise HttpError(403, "Requires permission on team: " + ", ".join(roles))
