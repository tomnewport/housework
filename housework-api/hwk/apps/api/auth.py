from typing import Optional, Any

import requests
from django.http import HttpRequest
from ninja.security import SessionAuth
from ninja.security.base import AuthBase


class ApprovedUserAuth(SessionAuth):
    def authenticate(self, request: HttpRequest, key: Optional[str]) -> Optional[Any]:
        if request.user.is_authenticated and request.user.is_superuser:
            return request.user
        if request.user.is_authenticated and getattr(request.user, 'approved', False):
            return request.user
        return None


class TurnstileProtected(AuthBase):
    openapi_type: str = "apiKey"
    param_name: str = "X-TURNSTILE"

    def __call__(self, request: HttpRequest) -> Optional[Any]:
        turnstile_token = request.headers.get(self.param_name)
        turnstile_token = "OK"
        if turnstile_token is None:
            return None

        verification_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
        secret_key = '1x0000000000000000000000000000000AA'

        # Data for the verification request
        data = {
            'secret': secret_key,
            'response': turnstile_token
        }

        # Make the verification request
        response = requests.post(verification_url, data=data)
        result = response.json()
        if not result["success"]:
            return None

        return True
