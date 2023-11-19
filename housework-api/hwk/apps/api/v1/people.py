from datetime import datetime
from typing import List, Optional, Any, Dict

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from ninja import Router, Schema, Body, ModelSchema
from ninja.pagination import paginate
from pydantic import EmailStr

from hwk.apps.api.auth import TurnstileProtected, HeaderUserAuth
from hwk.apps.api.v1.schema import UserSchema, UserSelfSchema
from hwk.apps.people.models import HwkUser
from hwk.apps.teams.models import Membership

people_router = Router(tags=["People"])


class UserEditSchema(Schema):
    full_name: Optional[str]
    short_name: Optional[str]
    password: Optional[str]


class UserResponseSchema(ModelSchema):
    has_usable_password: bool

    class Config:
        model = HwkUser
        model_fields = ["full_name", "short_name", "email"]


class UserListSchema(Schema):
    username: str
    full_name: Optional[str]
    short_name: Optional[str]
    email: Optional[str]
    approved: bool


class UserDetailSchema(Schema):
    username: str
    full_name: Optional[str]
    short_name: Optional[str]
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
        teams = Membership.objects.filter(user=request.user).values_list(
            "team", flat=True
        )
        users = HwkUser.objects.filter(memberships__team__in=teams).distinct()
    else:
        users = HwkUser.objects.filter(id=request.user.id)
    return users


@people_router.patch(
    "/users/self/",
    response=UserResponseSchema,
    auth=[HeaderUserAuth(require_approved=False)],
)
def update_user(request, data: UserEditSchema):
    for key, value in data.dict(exclude_unset=True).items():
        if key in ["full_name", "short_name"]:
            setattr(request.user, key, value)
        if key == "password":
            request.user.set_password(value)

    request.user.save()
    return request.user


@people_router.get(
    "/users/self/",
    response=Optional[UserSelfSchema],
    auth=[HeaderUserAuth(require_approved=False)],
)
def get_current_user(request):
    if not request.user.is_authenticated:
        return None

    return request.user


@people_router.put("/users/self/preferences", response=Optional[UserSelfSchema])
def set_current_user_preferences(request, preferences: Dict[str, Any] = Body({})):
    request.user.preferences = preferences
    request.user.save()

    return request.user


@people_router.post(
    "/users/{username}/approve",
    response={200: ActionResponse, 404: ActionResponse, 403: ActionResponse},
)
def approve_user(request, username: str):
    if not (
        request.user.is_superuser
        or Membership.objects.filter(user=request.user, role="Admin").exists()
    ):
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


@people_router.post(
    "/users/self/password",
    response={403: ActionResponse, 401: ActionResponse, 200: ActionResponse},
)
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
