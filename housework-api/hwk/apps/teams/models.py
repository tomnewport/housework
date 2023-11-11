from typing import Generator

from datetime import date, timedelta
from django.db import models
import uuid

from hwk.apps.people.models import HwkUser, Holiday


class HolidayPolicy(models.TextChoices):
    FIND_OTHER = 'FIND_OTHER', 'Try to find another assignee'
    FIRST_ASSIGNEE = 'WHEN_BACK', 'Give to first assignee when back'


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    policy_when_on_holiday = models.CharField(max_length=16, choices=HolidayPolicy.choices)

    policy_max_team_diff = models.PositiveSmallIntegerField(help_text="Maximum relative credit in team to consider for job assigner", default=600)
    policy_max_job_diff = models.PositiveSmallIntegerField(help_text="Maximum relative credit on a job to consider for job assigner", default=120)
    policy_team_credit_weight = models.PositiveSmallIntegerField(help_text="Weight given to relative credit within the team")
    policy_job_credit_weight = models.PositiveSmallIntegerField(help_text="Weight given to relative credit on each job")
    policy_random_weight = models.PositiveSmallIntegerField(help_text="Random weighting")

    def __str__(self):
        return self.name


class Membership(models.Model):
    class RoleChoices(models.TextChoices):
        Member = 'Member', 'Member'
        Applicant = 'Applicant', 'Applicant'
        Admin = 'Admin', 'Admin'

    user = models.ForeignKey(HwkUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=RoleChoices.choices)

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"

    def dates_not_on_holiday(self, dates: Generator[date, None, None]) -> Generator[date, None, None]:
        """
        Yields dates from the provided generator for which the associated HwkUser is not on holiday.

        :param dates: A generator that yields date objects.
        :return: A generator that yields date objects.
        """

        user = self.user

        # Retrieve all holiday periods for the user
        holidays = Holiday.objects.filter(user=user)

        # Convert holiday periods to a set of individual dates for efficient lookup
        holiday_dates = set()
        for holiday in holidays:
            current_date = holiday.from_time.date()
            while current_date <= holiday.to_time.date():
                holiday_dates.add(current_date)
                current_date += timedelta(days=1)

        # Yield dates not in the holiday set
        for current_date in dates:
            if current_date not in holiday_dates:
                yield current_date
