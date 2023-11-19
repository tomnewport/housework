from ninja import NinjaAPI

from hwk.apps.api.auth import HeaderUserAuth
from hwk.apps.api.v1 import api_v1

api = NinjaAPI(auth=HeaderUserAuth(), csrf=False)

api.add_router("v1/", api_v1)
