import json
from abc import abstractmethod
from datetime import date, timedelta, datetime
from enum import Enum
from typing import Generator, List, Tuple, Dict

from django.utils import timezone
from pydantic import BaseModel, constr, root_validator, ValidationError, validator

from hwk.apps.jobs.models import Job, JobScheduleRule, JobTrigger, JobConfig
from hwk.apps.people.models import HwkUser
from hwk.apps.teams.models import Membership


def generate_dates_from_today(delay=0) -> Generator[date, None, None]:
    """
    A generator that yields dates starting from today, continuing indefinitely.

    Yields:
        date: The next date starting from today.
    """
    current_date = date.today() + timedelta(days=delay + 1)
    while True:
        yield current_date
        current_date += timedelta(days=1)


class WeekDay(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class ValidEvent(Enum):
    closed = "closed"
    created = "created"
    due = "due"


class RuleFilter(BaseModel):
    @abstractmethod
    def __call__(
        self, trigger: Job, dates: Generator[date, None, None]
    ) -> Generator[date, None, None]:
        """"""


class RuleDayInWeek(RuleFilter):
    days: List[WeekDay]

    @validator('days')
    def check_days_not_empty(cls, v):
        if not v:
            raise ValueError("At least one day must be specified")
        return v

    @property
    def summary(self):
        # Joining the names of the days with commas
        if len(self.days) == 1:
            days = ", ".join(f"{day.value}s" for day in self.days)
            return f"On {days}"
        if len(self.days) > 1:
            days_pre = ", ".join(f"{day.value}s" for day in self.days[:-1])
            days_post = self.days[-1].value
            return f"On {days_pre} or {days_post}s"
        return "Never"

    def __call__(
        self, trigger: Job, dates: Generator[date, None, None]
    ) -> Generator[date, None, None]:
        # Map day names to weekday numbers
        day_to_num = {
            WeekDay.MONDAY: 0,
            WeekDay.TUESDAY: 1,
            WeekDay.WEDNESDAY: 2,
            WeekDay.THURSDAY: 3,
            WeekDay.FRIDAY: 4,
            WeekDay.SATURDAY: 5,
            WeekDay.SUNDAY: 6,
        }

        # Convert day names to numbers
        day_nums = [day_to_num[day] for day in self.days if day in day_to_num]

        # Yield dates where the weekday is in day_nums
        for day in dates:
            if day.weekday() in day_nums:
                yield day


class RuleDaysSince(RuleFilter):
    days: int
    event: ValidEvent

    def __call__(
        self, trigger: Job, dates: Generator[date, None, None]
    ) -> Generator[date, None, None]:
        event_date_attr = f"{self.event.value}_date"
        reference_date = getattr(trigger, event_date_attr, timezone.now()) or timezone.now()

        # Calculate the earliest date to start yielding from
        earliest_date = reference_date.date() + timedelta(days=self.days)

        # Yield dates that are on or after the earliest date
        for current_date in dates:
            if current_date >= earliest_date:
                yield current_date

    @property
    def summary(self):
        # Describing the rule based on the number of days
        return f"At least {self.days} day{'' if self.days == 1 else 's'} since the last job was {self.event.value}"


def format_date(month, day):
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    # Ensure month and day are within valid ranges
    if 1 <= month <= 12 and 1 <= day <= 31:
        month_name = month_names[month - 1]
    else:
        return "(invalid date)"

    # Determine the appropriate suffix for the day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    return f"{month_name} {day}{suffix}"


class RuleDayInYear(RuleFilter):
    gte: constr(regex=r"^\d{2}-\d{2}$")
    lte: constr(regex=r"^\d{2}-\d{2}$")
    _gte_tuple: Tuple[int, int] = None
    _lte_tuple: Tuple[int, int] = None

    @root_validator
    def parse_dates(cls, values):
        # Convert gte and lte to tuples (month, day)
        gte_month, gte_day = map(int, values['gte'].split('-'))
        lte_month, lte_day = map(int, values['lte'].split('-'))

        values['_gte_tuple'] = (gte_month, gte_day)
        values['_lte_tuple'] = (lte_month, lte_day)
        return values

    def is_date_within_range(self, current_date):
        month_day = (current_date.month, current_date.day)
        gte_tuple = self._gte_tuple
        lte_tuple = self._lte_tuple

        if gte_tuple <= lte_tuple:
            # Normal range (e.g., Apr 10 to Oct 31)
            return gte_tuple <= month_day <= lte_tuple
        else:
            # Inverted range (e.g., Nov 1 to Mar 31)
            return month_day >= gte_tuple or month_day <= lte_tuple

    def __call__(self, trigger: Job, dates: Generator[date, None, None]) -> Generator[date, None, None]:
        for current_date in dates:
            if self.is_date_within_range(current_date):
                yield current_date

    @property
    def summary(self):
        if self._gte_tuple > self._lte_tuple:
            return f"On or after {format_date(*self._gte_tuple)} and on or before {format_date(*self._lte_tuple)}"
        return f"Between {format_date(*self._gte_tuple)} and {format_date(*self._lte_tuple)}, inclusive."



def get_function(rule: JobScheduleRule):
    if rule.rule_type == JobScheduleRule.RuleType.DAYS_SINCE:
        return RuleDaysSince
    if rule.rule_type == JobScheduleRule.RuleType.DAY_IN_WEEK:
        return RuleDayInWeek
    if rule.rule_type == JobScheduleRule.RuleType.DAY_IN_YEAR:
        return RuleDayInYear


def validate_rule(rule: JobScheduleRule):
    function = get_function(rule)
    try:
        return True, function(**rule.params).summary
    except ValidationError as e:
        return False, str(e)


def schedule_for_user(trigger: JobTrigger, job: Job, membership: Membership):
    all_dates = generate_dates_from_today(delay=job.delay)
    available_dates = membership.dates_not_on_holiday(all_dates)

    for rule in trigger.rules.all():
        function = get_function(rule)
        with_args = function(**rule.params)
        available_dates = with_args(job, available_dates)

    return next(available_dates)


class DryRunOutcome(BaseModel):
    created_job: JobConfig
    proposed_date: date
    trigger: JobTrigger

    class Config:
        arbitrary_types_allowed = True


def dry_run_trigger(trigger: JobTrigger, job: Job, delay: int) -> DryRunOutcome:
    rules = trigger.rules.all()

    available_dates: Generator[date, None, None] = generate_dates_from_today(delay=delay)
    for rule in rules:
        function = get_function(rule)
        with_args = function(**rule.params)
        available_dates = with_args(job, available_dates)

    return DryRunOutcome(trigger=trigger, created_job=trigger.create_config, proposed_date=next(available_dates))


def dry_run(job: Job, delay: int, action: str):
    config = job.job_config
    filter_params = {
        f"lifecycle_{action.lower()}": True,
    }
    triggers = JobTrigger.objects.filter(**filter_params)
    if config is None:
        return []
    return [dry_run_trigger(job=job, trigger=_, delay=delay) for _ in config.trigger_from.filter(**filter_params)]
