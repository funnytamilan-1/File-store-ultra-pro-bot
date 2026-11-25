import hashlib
import hmac
import json
from urllib.parse import urlencode
from unittest.mock import patch
from utils import webapp_verify


def make_init_data(user, token, auth_date):
    values = {"auth_date": str(auth_date), "user": json.dumps(user, separators=(",", ":"))}
    check = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    values["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(values)


def test_valid_webapp_init_data_returns_user():
    token = "123456:bot-token"
    user = {"id": 12345, "first_name": "Test"}
    with patch.object(webapp_verify, "BOT_TOKEN", token), patch.object(webapp_verify.time, "time", return_value=2000):
        result = webapp_verify.get_verified_webapp_user(make_init_data(user, token, 1999))
    assert result == user


def test_expired_webapp_init_data_is_rejected():
    token = "123456:bot-token"
    user = {"id": 12345}
    with patch.object(webapp_verify, "BOT_TOKEN", token), patch.object(webapp_verify.time, "time", return_value=100000):
        result = webapp_verify.get_verified_webapp_user(make_init_data(user, token, 1))
    assert result is None
