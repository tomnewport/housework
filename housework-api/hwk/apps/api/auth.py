from importlib import import_module
from typing import Optional, Any

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from ninja.security import APIKeyHeader
from ninja.security.base import AuthBase


class HeaderUserAuth(APIKeyHeader):
    param_name = "X-SessionID"

    def __init__(self, require_user: bool = True, require_approved: bool = False):
        self.require_approved = require_approved
        self.require_user = require_user
        super().__init__()
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        header_session_id = request.headers.get('X-SessionID')
        if not self.require_user:
            request.session = self.SessionStore(header_session_id)
            return True

        User = get_user_model()
        if header_session_id:
            try:
                request.session = self.SessionStore(header_session_id)
                user_id = request.session.get('_auth_user_id')
                user = User.objects.get(id=user_id)
                request.user = user

            except (Session.DoesNotExist, User.DoesNotExist):
                return None
        else:
            user = request.user

        if user.is_authenticated:
            if user.is_superuser:
                return user

            if self.require_approved:
                if not getattr(user, "approved", False):
                    return None

            return user

        return None


class TurnstileProtected(AuthBase):
    openapi_type: str = "apiKey"
    param_name: str = "X-TURNSTILE"

    def __call__(self, request: HttpRequest) -> Optional[Any]:
        turnstile_token = request.headers.get(self.param_name)
        turnstile_token = "OK"
        if turnstile_token is None:
            return None

        verification_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        secret_key = "1x0000000000000000000000000000000AA"

        # Data for the verification request
        data = {"secret": secret_key, "response": turnstile_token}

        # Make the verification request
        response = requests.post(verification_url, data=data)
        result = response.json()
        if not result["success"]:
            return None

        return True
