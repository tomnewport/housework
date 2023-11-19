from datetime import timedelta, datetime
from typing import List

from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from ninja import Router, Schema, Body
from ninja.errors import HttpError
from django.core.mail import send_mail
import secrets
import string

from pydantic import EmailStr

from hwk.apps.api.auth import TurnstileProtected, HeaderUserAuth
from hwk.apps.people.models import HwkUser
from hwk.apps.teams.models import Membership, Team, MembershipRole

auth_router = Router(tags=["Authentication"])


def generate_secure_sequence(length=6):
    # Select the lowercase alphabet
    alphabet = string.ascii_lowercase

    # Generate a secure random string of specified length
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class LoginSchema(Schema):
    username: str
    password: str


class OTPSendRequest(Schema):
    sub: EmailStr


class OTPRespondRequest(Schema):
    code: str


@auth_router.get("/session")
def get_session(request):
    return dict(request.session)


@auth_router.post("/otp/send", auth=[TurnstileProtected()])
def send_otp(request, data: OTPSendRequest = Body(...)):
    otp = generate_secure_sequence()

    request.session["otp.challenge.sub"] = data.sub
    request.session["otp.challenge.open"] = True
    request.session["otp.challenge.code"] = otp
    request.session["otp.challenge.expires"] = (timezone.now() + timedelta(minutes=5)).isoformat()
    print("OTP is", otp)
    # send_mail(
    #     "Subject here",
    #     "Here is the message.",
    #     "from@example.com",
    #     [sub],
    #     fail_silently=False,
    # )
    request.session.save()
    return {
        "x-sessionid": request.session.session_key,
    }


@auth_router.post("/otp/respond", auth=[HeaderUserAuth(require_user=False)])
def respond_otp(request, data: OTPRespondRequest = Body(...)):
    request.session["otp.challenge.attempts"] = request.session.get("otp.challenge.attempts", 0) + 1
    print(dict(request.session))
    otp_challenge_sub = request.session.get("otp.challenge.sub", None)
    otp_challenge_open = request.session.get("otp.challenge.open", False)
    otp_challenge_code = request.session.get("otp.challenge.code", None)
    otp_challenge_expires_str = request.session.get("otp.challenge.expires", "")
    if "T" in otp_challenge_expires_str:
        otp_challenge_expires = datetime.fromisoformat(otp_challenge_expires_str)
    else:
        otp_challenge_expires = datetime.fromisoformat("2000-01-01T10:00:00")

    if request.session.get("otp.challenge.attempts", 0) > 5:
        raise HttpError(403, "Too many failed attempts")

    if not otp_challenge_open:
        raise HttpError(403, "OTP challenge not open")

    if otp_challenge_expires < timezone.now():
        raise HttpError(403, "OTP challenge expired")

    if otp_challenge_code is None:
        raise HttpError(403, "OTP challenge not set")

    if otp_challenge_code != data.code:
        raise HttpError(403, "OTP not matched")

    if otp_challenge_sub is None:
        raise HttpError(401, "OTP sub not set")

    try:
        user = HwkUser.objects.get(email=otp_challenge_sub)
    except HwkUser.DoesNotExist:
        user = HwkUser.objects.create_user(username=otp_challenge_sub, email=otp_challenge_sub)

    login(request, user)

    request.session.save()

    return {
        "x-sessionid": request.session.session_key,
    }

@auth_router.post("/session", auth=[TurnstileProtected()])
@csrf_exempt
def login_user(request, data: LoginSchema):
    user = authenticate(request, username=data.username, password=data.password)

    if user is not None:
        login(request, user)
        return {
            "x-csrftoken": get_token(request),
            "x-sessionid": request.session.session_key,
        }
    else:
        return {"success": False, "message": "Invalid username or password."}


@auth_router.delete("/session")
@csrf_exempt
def logout_user(request):
    logout(request)
    return {"success": True, "message": "User successfully logged out."}


def has_team_permission_or_superuser(
    user, team_id, roles: List[MembershipRole]
) -> bool:
    if user.is_superuser:
        try:
            return Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise HttpError(404, "Team does not exist")

    membership = Membership.objects.filter(user=user, team_id=team_id).first()

    if membership.role not in roles:
        raise HttpError(403, "Requires permission on team: " + ", ".join(roles))
