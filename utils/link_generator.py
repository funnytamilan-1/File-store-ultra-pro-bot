import hashlib
import hmac
import time
from config import SECRET_KEY


def generate_secure_link(file_id: str, expiry_seconds: int = 3600) -> str:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY must be configured before generating secure links.")
    if int(expiry_seconds) < 1:
        raise ValueError("Link expiry must be positive.")
    expire_at = int(time.time()) + int(expiry_seconds)
    message = f"{file_id}:{expire_at}".encode()
    signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()
    return f"{file_id}?exp={expire_at}&sig={signature}"


def verify_secure_link(file_id: str, exp: int, sig: str) -> bool:
    if not SECRET_KEY or not sig:
        return False
    try:
        expiry = int(exp)
    except (TypeError, ValueError):
        return False
    if int(time.time()) > expiry:
        return False
    message = f"{file_id}:{expiry}".encode()
    expected = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, str(sig))
