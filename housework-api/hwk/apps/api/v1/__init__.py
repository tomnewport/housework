from django.http import HttpRequest
from ninja import Router
from ninja.security import SessionAuth

from hwk.apps.api.v1.auth import auth_router
from hwk.apps.api.v1.job import job_router
from hwk.apps.api.v1.notification import notification_router
from hwk.apps.api.v1.people import people_router


from typing import Any, Optional

from hwk.apps.api.v1.team import team_router


api_v1 = Router()

api_v1.add_router("auth/", auth_router)
api_v1.add_router("people/", people_router)
api_v1.add_router("teams/", team_router)
api_v1.add_router("/", job_router)
api_v1.add_router("notifications/", notification_router)
