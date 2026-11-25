import time

_RATE_LIMIT = {}
LIMIT_SECONDS = 5
MAX_TRACKED_USERS = 10000


async def check_rate_limit(user_id: int):
    now = time.monotonic()
    user_id = int(user_id)
    last = _RATE_LIMIT.get(user_id)
    if last is not None and now - last < LIMIT_SECONDS:
        return False
    _RATE_LIMIT[user_id] = now
    if len(_RATE_LIMIT) > MAX_TRACKED_USERS:
        cutoff = now - LIMIT_SECONDS
        for key, timestamp in list(_RATE_LIMIT.items()):
            if timestamp < cutoff:
                _RATE_LIMIT.pop(key, None)
        if len(_RATE_LIMIT) > MAX_TRACKED_USERS:
            for key in list(_RATE_LIMIT)[: len(_RATE_LIMIT) - MAX_TRACKED_USERS]:
                _RATE_LIMIT.pop(key, None)
    return True
