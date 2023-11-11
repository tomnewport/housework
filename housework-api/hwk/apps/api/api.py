from ninja import NinjaAPI
from ninja.security import SessionAuth

from hwk.apps.api.v1 import api_v1

api = NinjaAPI(auth=SessionAuth(), csrf=True)

api.add_router("v1/", api_v1)
