from django.contrib import admin

from hwk.apps.teams.models import Team, Membership

admin.site.register(Team)
admin.site.register(Membership)
