from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from hwk.apps.people.models import HwkUser

admin.site.register(HwkUser, UserAdmin)
