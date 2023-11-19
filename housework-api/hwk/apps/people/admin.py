from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from hwk.apps.people.models import HwkUser, Holiday


@admin.register(HwkUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(Holiday)
