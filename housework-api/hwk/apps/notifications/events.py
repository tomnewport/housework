from enum import Enum


class EventType(Enum):
    JOB_SCHEDULED = "JOB_SCHEDULED", "A job was scheduled but not open"
    JOB_OPEN = "JOB_OPEN", "Job is ready to work on"
    JOB_OVERDUE = "JOB_OVERDUE", "Job is overdue"
    JOB_COMPLETE = "JOB_COMPLETE", "Job is complete"
    JOB_CANCELLED = "JOB_CANCELLED", "Job is cancelled"
