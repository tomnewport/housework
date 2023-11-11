from datetime import datetime
from typing import List, Optional

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from ninja import Router, Schema
from ninja.pagination import paginate
from pydantic import EmailStr

from hwk.apps.api.auth import TurnstileProtected, ApprovedUserAuth
from hwk.apps.api.v1.schema import UserSchema
from hwk.apps.people.models import HwkUser
from hwk.apps.teams.models import Membership

people_router = Router(tags=["People"])


class UserCreateSchema(Schema):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserResponseSchema(Schema):
    username: str
    first_name: str
    last_name: str
    email: str
    approved: bool


class UserListSchema(Schema):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    approved: bool


class UserDetailSchema(Schema):
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    logged_in_since: datetime
    session_expires: datetime
    approved: bool


class ActionResponse(Schema):
    success: bool
    message: str


@people_router.get("/users/", response=List[UserListSchema])
@paginate
def get_users(request):
    if not request.user.is_authenticated:
        # If no user is logged in, return an empty list
        return []
    if request.user.is_superuser:
        users = HwkUser.objects.all()
    elif request.user.approved:
        teams = Membership.objects.filter(user=request.user).values_list('team', flat=True)
        users = HwkUser.objects.filter(
            memberships__team__in=teams
        ).distinct()
    else:
        users = HwkUser.objects.filter(id=request.user.id)
    return users


@people_router.post("/users/", response=UserResponseSchema, auth=[TurnstileProtected(), ApprovedUserAuth()])
def create_user(request, user: UserCreateSchema):
    user = HwkUser(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=make_password(user.password),
        approved=False  # Set approved to False by default
    )
    user.save()
    return user


@people_router.get("/users/self/", response=Optional[UserSchema], auth=[TurnstileProtected(), ApprovedUserAuth()])
def get_current_user(request):
    if not request.user.is_authenticated:
        return None

    return request.user


@people_router.post("/users/{username}/approve", response={200: ActionResponse, 404: ActionResponse, 403: ActionResponse})
def approve_user(request, username: str):
    if not (request.user.is_superuser or Membership.objects.filter(user=request.user, role='Admin').exists()):
        return 403, {"success": False, "message": "Permission denied"}

    try:
        user_to_approve = HwkUser.objects.get(username=username)
        user_to_approve.approved = True
        user_to_approve.save()
        return {"success": True, "message": f"User {username} approved."}

    except HwkUser.DoesNotExist:
        return 404, {"success": False, "message": "User not found"}


class PasswordChangeModel(Schema):
    current_password: str
    new_password: str


@people_router.post("/users/self/password", response={403: ActionResponse, 401: ActionResponse, 200: ActionResponse})
def change_password(request, password_data: PasswordChangeModel):
    user = request.user
    if not user.is_authenticated:
        return 401, {"success": False, "message": "User not authenticated"}

    # Verify current password
    if not check_password(password_data.current_password, user.password):
        return 403, {"success": False, "message": "Incorrect current password"}

    # Set new password
    user.set_password(password_data.new_password)
    user.save()
    return {"success": True, "message": "Password updated successfully"}
