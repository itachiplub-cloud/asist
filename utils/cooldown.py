import time
from collections import deque
from config import MAX_INVITES_PER_HOUR


class CooldownManager:
    def __init__(self):
        self.timestamps = deque()

    def record_invite(self):
        self.timestamps.append(time.time())

    def can_invite(self) -> bool:
        now = time.time()
        while self.timestamps and now - self.timestamps[0] > 3600:
            self.timestamps.popleft()
        return len(self.timestamps) < MAX_INVITES_PER_HOUR

    def remaining_quota(self) -> int:
        now = time.time()
        while self.timestamps and now - self.timestamps[0] > 3600:
            self.timestamps.popleft()
        return max(0, MAX_INVITES_PER_HOUR - len(self.timestamps))

    def reset(self):
        self.timestamps.clear()
