import time
from enum import Enum
import datetime

class Task(object):
    def __init__(self, func, delay, start_date, args=()):
        self.args = args
        self.function = func
        self.delay = delay
        date_object = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        self.next_run = date_object.timestamp()

    def shouldRun(self):
        return time.time() >= self.next_run

    async def run(self):
        self.function(*(self.args))
        self.next_run += self.delay

class SchedulingFrequency(str, Enum):
    TEST = "test"
    Daily = "Daily"
    Weekly = "Weekly"
    Monthly = "Monthly"
    Yearly = "Yearly"

    @property
    def seconds(self):
        """Map each frequency name to its corresponding period in seconds."""
        if self == SchedulingFrequency.TEST:
            return 10  # 10 seconds just for test
        if self == SchedulingFrequency.Daily:
            return 86400  # 24 hours
        elif self == SchedulingFrequency.Weekly:
            return 604800  # 7 days
        elif self == SchedulingFrequency.Monthly:
            return 2592000  # 30 days
        elif self == SchedulingFrequency.Yearly:
            return 31536000  # 1 year
        return None