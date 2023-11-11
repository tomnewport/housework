from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from hwk.apps.jobs.assigner import create_job_from_trigger
from hwk.apps.jobs.models import JobConfig, JobTrigger, JobLifecycle, Job, Credit, JobScheduleRule
from hwk.apps.people.models import HwkUser, Holiday
from hwk.apps.teams.models import Team, Membership


def setup_db():
    class TestData:
        user_1 = HwkUser(username="user_1", first_name="User", last_name="One")
        user_1.save()
        user_2 = HwkUser(username="user_2", first_name="User", last_name="Two")
        user_2.save()

        team = Team(
            name="Test Team",
            policy_team_credit_weight=10,
            policy_job_credit_weight=10,
            policy_random_weight=10,
        )
        team.save()

        user_1_membership = Membership(
            team=team,
            role=Membership.RoleChoices.Admin,
            user=user_1
        )
        user_1_membership.save()
        user_2_membership = Membership(
            team=team,
            role=Membership.RoleChoices.Admin,
            user=user_2
        )
        user_2_membership.save()

        user_1_holiday = Holiday(
            user=user_1,
            from_time=timezone.now(),
            to_time=timezone.now() + timedelta(days=10)
        )
        user_1_holiday.save()

        dishwasher_config = JobConfig(
            name="Load the dishwasher",
            default_credit=10,
            team=team,
        )
        dishwasher_config.save()

        laundry_config = JobConfig(
            name="Load of laundry",
            default_credit=20,
            team=team,
        )
        laundry_config.save()

        dishwasher_trigger = JobTrigger(
            from_config=dishwasher_config,
            create_config=dishwasher_config,
            lifecycle=JobLifecycle.COMPLETE,
            urgent=False,
        )
        dishwasher_trigger.save()

        dishwasher_rule = JobScheduleRule(
            trigger=dishwasher_trigger,
            rule_type=JobScheduleRule.RuleType.DAYS_SINCE,
            params='{"event": "closed", "days": 4}'
        )
        dishwasher_rule.save()

        dishwasher_previous = Job(
            job_config=dishwasher_config,
            name=dishwasher_config.name,
            default_credit=dishwasher_config.default_credit,
            closed_date=timezone.now(),
            assignee=user_1_membership,
        )
        dishwasher_previous.save()

        laundry_previous = Job(
            job_config=laundry_config,
            name=laundry_config.name,
            default_credit=laundry_config.default_credit,
            closed_date=timezone.now(),
            assignee=user_2_membership,
        )
        laundry_previous.save()

        Credit(
            person=user_1_membership,
            amount=10,
            job=dishwasher_previous
        ).save()

        Credit(
            person=user_2_membership,
            amount=20,
            job=laundry_previous
        ).save()

    return TestData


expected_scheduler = """# Scheduling Load the dishwasher

## User One

- Available from: 2023-01-12
- Has 10 credit on job Load the dishwasher
- Has 10 credit in team Test Team
- Gets 0.20 random value

## User Two

- Available from: 2023-01-05
- Has 0 credit on job Load the dishwasher
- Has 20 credit in team Test Team
- Gets 0.30 random value

## Scoring

| Candidate | Random | Team | Job | Score |
| - | - | - | - | - |
| User One |0.20 * 10 |0.00 * 10 |0.08 * 10 |2.83 |
| User Two |0.30 * 10 |0.02 * 10 |0.00 * 10 |3.17 |

## Result

User One is selected.
"""

expected_scheduler_urgent = """# Scheduling Load the dishwasher

## User One

- Available from: 2023-01-12
- Has 10 credit on job Load the dishwasher
- Has 10 credit in team Test Team
- Gets 0.20 random value

## User Two

- Available from: 2023-01-05
- Has 0 credit on job Load the dishwasher
- Has 20 credit in team Test Team
- Gets 0.30 random value

## Availability

Some candidates were removed due to lack of availability.

## Scoring

| Candidate | Random | Team | Job | Score |
| - | - | - | - | - |
| User Two |0.30 * 10 |0.02 * 10 |0.00 * 10 |3.17 |

## Result

User Two is selected.
"""


class AssignerTest(TestCase):
    maxDiff = None

    @freeze_time("2023-01-01")
    @patch("hwk.apps.jobs.assigner.random", side_effect=[0.2, 0.3])
    def test_create_job_from_trigger(self, _):
        data = setup_db()

        job = create_job_from_trigger(data.dishwasher_previous, data.dishwasher_trigger)
        self.assertEqual(job.description, expected_scheduler)

    @freeze_time("2023-01-01")
    @patch("hwk.apps.jobs.assigner.random", side_effect=[0.2, 0.3])
    def test_create_job_from_trigger_urgent(self, _):
        data = setup_db()
        data.dishwasher_trigger.urgent = True
        data.dishwasher_trigger.save()

        job = create_job_from_trigger(data.dishwasher_previous, data.dishwasher_trigger)

        self.assertEqual(job.description, expected_scheduler_urgent)

    @freeze_time("2023-01-01")
    @patch("hwk.apps.jobs.assigner.random", side_effect=[0.2, 0.3])
    def test_create_job_from_trigger_urgent_no_holiday(self, _):
        data = setup_db()
        data.user_1_holiday.delete()
        data.dishwasher_trigger.urgent = True
        data.dishwasher_trigger.save()

        job = create_job_from_trigger(data.dishwasher_previous, data.dishwasher_trigger)

        self.assertEqual(job.description, expected_scheduler.replace("Available from: 2023-01-12", "Available from: 2023-01-05"))



