import json
from datetime import date, timedelta
from typing import Generator, List

from hwk.apps.jobs.models import Job, JobScheduleRule, JobTrigger
from hwk.apps.teams.models import Membership


def generate_dates_from_today() -> Generator[date, None, None]:
    """
    A generator that yields dates starting from today, continuing indefinitely.

    Yields:
        date: The next date starting from today.
    """
    current_date = date.today()
    while True:
        yield current_date
        current_date += timedelta(days=1)


def rule_day_in_week(dates: Generator[date, None, None], trigger: Job, days: List[str]) -> Generator[date, None, None]:
    """
    Yields dates from the generator where the weekday matches one of the days specified in the days list.

    Parameters:
        dates (Generator[date, None, None]): A generator that yields dates.
        trigger (Job): The Job object (unused in this function but kept for consistency with the signature).
        days (List[str]): A list of day names, like ["Monday", "Tuesday"].

    Yields:
        date: Dates where the weekday matches a day in the days list.
    """
    # Map day names to weekday numbers
    day_to_num = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}

    # Convert day names to numbers
    day_nums = [day_to_num[day] for day in days if day in day_to_num]

    # Yield dates where the weekday is in day_nums
    for day in dates:
        if day.weekday() in day_nums:
            yield day


def rule_days_since(dates: Generator[date, None, None], trigger: Job, event: str, days: int):
    """
    Yields dates from the generator 'dates' that are 'days' after the 'event' date in 'trigger'.

    :param dates: Generator of dates.
    :param trigger: Object containing the event date.
    :param event: String attribute name in 'trigger' to find the event date.
    :param days: Number of days after the event date to start yielding dates.

    :raises TypeError: If the event date in 'trigger' is not a valid date.
    """
    event_date_attr = f"{event}_date"
    reference_date = getattr(trigger, event_date_attr, None)

    # Validate the reference date
    if not isinstance(reference_date, date):
        raise TypeError(f"{event_date_attr} in trigger is not a valid date.")

    # Calculate the earliest date to start yielding from
    earliest_date = reference_date.date() + timedelta(days=days)

    # Yield dates that are on or after the earliest date
    for current_date in dates:
        if current_date >= earliest_date:
            yield current_date


def rule_day_in_year(dates: Generator[date, None, None], trigger: Job, gte: str, lte: str) -> Generator[date, None, None]:
    """
    Yields dates from the generator filtered by a range defined by gte and lte tuples.

    Parameters:
        dates (Generator[date, None, None]): A generator that yields dates.
        trigger (Job): The Job object (unused in this function but kept for consistency).
        gte (str): Tuple of month name and day number, representing the start of the range.
        lte (str): Tuple of month name and day number, representing the end of the range.

    Yields:
        date: Dates within the specified range.
    """

    gte_date = tuple(int(x) for x in gte.split("-"))
    lte_date = tuple(int(x) for x in lte.split("-"))
    inner_date = lte_date > gte_date

    for current_date in dates:
        date_tuple = (current_date.month, current_date.day)
        if inner_date:
            if lte_date >= date_tuple >= gte_date:
                yield date
        else:
            if date_tuple >= gte_date or date_tuple <= lte_date:
                yield date


def get_function(rule: JobScheduleRule):
    if rule.rule_type == JobScheduleRule.RuleType.DAYS_SINCE:
        return rule_days_since
    if rule.rule_type == JobScheduleRule.RuleType.DAY_IN_WEEK:
        return rule_day_in_week
    if rule.rule_type == JobScheduleRule.RuleType.DAY_IN_YEAR:
        return rule_day_in_year


def get_arguments(rule: JobScheduleRule):
    return json.loads(rule.params)


def schedule_for_user(trigger: JobTrigger, job: Job, membership: Membership):
    all_dates = generate_dates_from_today()
    available_dates = membership.dates_not_on_holiday(all_dates)

    for rule in trigger.jobschedulerule_set.all():
        function = get_function(rule)
        args = get_arguments(rule)
        available_dates = function(available_dates, job, **args)

    return next(available_dates)
