import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl
from config import BOT_TOKEN


def get_verified_webapp_user(init_data: str, max_age_seconds: int = 86400):
    """Return the signed Telegram user payload, or None when initData is invalid."""
    if not init_data or not BOT_TOKEN:
        return None
    try:
        values = dict(parse_qsl(init_data, keep_blank_values=True, strict_parsing=True))
        received_hash = values.pop("hash")
        auth_date = int(values.get("auth_date", "0"))
        now = int(time.time())
        if auth_date > now + 60 or now - auth_date > max_age_seconds:
            return None
        data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None
        user = json.loads(values.get("user", "{}"))
        return user if isinstance(user, dict) and user.get("id") else None
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def verify_telegram_webapp(init_data: str) -> bool:
    return get_verified_webapp_user(init_data) is not None
