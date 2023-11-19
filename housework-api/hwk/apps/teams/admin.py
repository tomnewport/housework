from django.contrib import admin

from hwk.apps.teams.models import Team, Membership, Invitation

admin.site.register(Team)
admin.site.register(Membership)
admin.site.register(Invitation)
