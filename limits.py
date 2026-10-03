import time
from collections import defaultdict, deque
from datetime import date
from typing import Optional

PER_VISITOR_LIMIT = 5      # messages per visitor...
PER_VISITOR_WINDOW = 600   # ...in 10 minutes (600 seconds)
DAILY_LIMIT = 200          # messages per day for the whole demo

_visits = defaultdict(deque)
_daily = {"day": date.today(), "count": 0}


# Returns None if the visitor may continue, or a message explaining why not
def check_limits(visitor: str) -> Optional[str]:
    now = time.time()

    if _daily["day"] != date.today():
        _daily["day"] = date.today()
        _daily["count"] = 0

    if _daily["count"] >= DAILY_LIMIT:
        return "The demo has reached its daily limit. Please come back tomorrow."

    visits = _visits[visitor]
    while visits and now - visits[0] > PER_VISITOR_WINDOW:
        visits.popleft()

    if len(visits) >= PER_VISITOR_LIMIT:
        return "You've sent quite a few messages. Please wait a few minutes and try again."

    visits.append(now)
    _daily["count"] += 1
    return None