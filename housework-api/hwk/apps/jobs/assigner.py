from datetime import datetime, time
from random import random

from django.db.models import Sum
from django.utils import timezone

from hwk.apps.jobs.models import JobTrigger, Job, Credit
from hwk.apps.jobs.utils import schedule_for_user
from hwk.apps.teams.models import HolidayPolicy


def normalise(data, key, max_value):
    min_value = min(_[key] for _ in data)
    for item in data:
        item["normed_" + key] = min(1, (item[key] - min_value) / max_value)


def create_job_from_trigger(job: Job, trigger: JobTrigger):
    explainer = ""
    explainer += f"# Scheduling {trigger.create_config.name}\n"
    team = trigger.from_config.team
    available = team.memberships.all()

    workers = []

    for worker in available:
        available_date = schedule_for_user(membership=worker, trigger=trigger, job=job)
        worker_credit = Credit.objects.filter(person=worker)
        team_balance = worker_credit.aggregate(total=Sum('amount'))['total']
        job_balance = worker_credit.filter(job__job_config=job.job_config).aggregate(total=Sum('amount'))['total']
        random_value = random()
        explainer += f"\n## {worker.user.first_name} {worker.user.last_name}\n\n"
        explainer += f"- Available from: {available_date}\n"
        explainer += f"- Has {job_balance or 0} credit on job {job.name}\n"
        explainer += f"- Has {team_balance or 0} credit in team {team.name}\n"
        explainer += f"- Gets {random_value:.2f} random value\n"
        workers.append(dict(
            worker=worker,
            available_date=available_date,
            team_balance=team_balance or 0,
            job_balance=job_balance or 0,
            random_value=random_value,
        ))

    normalise(workers, "team_balance", team.policy_max_team_diff)
    normalise(workers, "job_balance", team.policy_max_job_diff)

    earliest_date = min(_["available_date"] for _ in workers)

    if trigger.urgent or team.policy_when_on_holiday == HolidayPolicy.FIND_OTHER:
        available_workers = [_ for _ in workers if _["available_date"] == earliest_date]
        if len(available_workers) < len(workers):
            workers = available_workers
            explainer += "\n## Availability\n\nSome candidates were removed due to lack of availability.\n"

    explainer += "\n## Scoring\n\n| Candidate | Random | Team | Job | Score |\n| - | - | - | - | - |\n"
    for worker in workers:
        weighted = worker["random_value"] * team.policy_random_weight
        weighted += worker["normed_team_balance"] * team.policy_team_credit_weight
        weighted += worker["normed_job_balance"] * team.policy_job_credit_weight
        explainer += f"| {worker['worker'].user} |"
        explainer += f"{worker['random_value']:.2f} * {team.policy_random_weight} |"
        explainer += f"{worker['normed_team_balance']:.2f} * {team.policy_team_credit_weight} |"
        explainer += f"{worker['normed_job_balance']:.2f} * {team.policy_job_credit_weight} |"
        explainer += f"{weighted:.2f} |\n"
        worker["score"] = weighted

    selected = sorted(workers, key=lambda _: _["score"])[0]

    explainer += f"\n## Result\n\n{selected['worker'].user} is selected.\n"

    result = Job(
        name=trigger.create_config.name,
        description=explainer,
        job_config=trigger.create_config,
        is_priority=trigger.urgent,
        due_date=timezone.make_aware(
            datetime.combine(selected['available_date'], time(23, 30)),
            timezone.get_current_timezone()
        ),
        assignee=selected['worker'],
        default_credit=trigger.create_config.default_credit,
    )
    result.save()
    return result
