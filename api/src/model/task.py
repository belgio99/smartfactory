import time
from enum import Enum

class Task(object):
    def __init__(self, func, delay, args=()):
        self.args = args
        self.function = func
        self.delay = delay
        self.next_run = time.time() + self.delay

    def shouldRun(self):
        return time.time() >= self.next_run

    async def run(self):
        self.function(*(self.args))
        self.next_run += self.delay

class SchedulingFrequency(Enum):
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