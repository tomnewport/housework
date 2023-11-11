import json
from abc import abstractmethod
from datetime import date, timedelta
from enum import Enum
from typing import Generator, List, Tuple

from pydantic import BaseModel, constr, root_validator

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


class WeekDay(Enum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'


class ValidEvent(Enum):
    CLOSED = 'closed'
    CREATED = 'created'
    DUE = 'due'


class RuleFilter(BaseModel):
    @abstractmethod
    def __call__(self, trigger: Job, dates: Generator[date, None, None]) -> Generator[date, None, None]:
        """"""


class RuleDayInWeek(RuleFilter):
    days: List[WeekDay]

    def __call__(self, trigger: Job, dates: Generator[date, None, None]) -> Generator[date, None, None]:
        # Map day names to weekday numbers
        day_to_num = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}

        # Convert day names to numbers
        day_nums = [day_to_num[day] for day in self.days if day in day_to_num]

        # Yield dates where the weekday is in day_nums
        for day in dates:
            if day.weekday() in day_nums:
                yield day


class RuleDaysSince(RuleFilter):
    days: int
    event: ValidEvent

    def __call__(self, trigger: Job, dates: Generator[date, None, None]) -> Generator[date, None, None]:
        event_date_attr = f"{self.event}_date"
        reference_date = getattr(trigger, event_date_attr, None)

        # Validate the reference date
        if not isinstance(reference_date, date):
            raise TypeError(f"{event_date_attr} in trigger is not a valid date.")

        # Calculate the earliest date to start yielding from
        earliest_date = reference_date.date() + timedelta(days=self.days)

        # Yield dates that are on or after the earliest date
        for current_date in dates:
            if current_date >= earliest_date:
                yield current_date


class DayAndMonth(BaseModel):
    value: constr(regex=r'^\d{2}-\d{2}$')


class RuleDayInYear(RuleFilter):
    gte: constr(regex=r'^\d{2}-\d{2}$')
    lte: constr(regex=r'^\d{2}-\d{2}$')
    _gte_tuple: Tuple[int, int] = None
    _lte_tuple: Tuple[int, int] = None


def get_function(rule: JobScheduleRule):
    if rule.rule_type == JobScheduleRule.RuleType.DAYS_SINCE:
        return RuleDaysSince
    if rule.rule_type == JobScheduleRule.RuleType.DAY_IN_WEEK:
        return RuleDayInWeek
    if rule.rule_type == JobScheduleRule.RuleType.DAY_IN_YEAR:
        return RuleDayInYear


def schedule_for_user(trigger: JobTrigger, job: Job, membership: Membership):
    all_dates = generate_dates_from_today()
    available_dates = membership.dates_not_on_holiday(all_dates)

    for rule in trigger.jobschedulerule_set.all():
        function = get_function(rule)
        with_args = function(**json.loads(rule.params))
        available_dates = with_args(job, available_dates)

    return next(available_dates)
