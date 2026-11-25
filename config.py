import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)
    return int(value) if value not in (None, "") else default


API_ID = _env_int("API_ID")
API_HASH = os.getenv("API_HASH", "").strip()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_ID = _env_int("OWNER_ID")
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "").lstrip("@").strip()

MONGO_URI = os.getenv("MONGO_URI", "").strip()
DATABASE_NAME = os.getenv("DATABASE_NAME", "file_store_bot").strip()

WEB_URL = os.getenv("WEB_URL", "http://localhost:8000").rstrip("/")
DOMAIN = os.getenv("DOMAIN", WEB_URL).rstrip("/")
ADMIN_PANEL_PATH = os.getenv("ADMIN_PANEL_PATH", "/admin").strip() or "/admin"
STREAM_PATH = os.getenv("STREAM_PATH", "/file").strip() or "/file"
ADMIN_PANEL_URL = f"{DOMAIN}{ADMIN_PANEL_PATH}"
STREAM_BASE_URL = f"{DOMAIN}{STREAM_PATH}"

START_PHOTO = os.getenv("START_PHOTO", os.getenv("START_IMAGE_URL", "")).strip()
START_IMAGE_URL = START_PHOTO
START_CAPTION = os.getenv(
    "START_CAPTION",
    "Welcome {first} to Ultra File Store Pro 🚀"
)

SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", SECRET_KEY).strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
LOG_CHANNEL_ID = _env_int("LOG_CHANNEL_ID")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() in {"1", "true", "yes"}
HOST = os.getenv("HOST", "0.0.0.0")
PORT = _env_int("PORT", 8000)
DEBUG = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"}
WORKERS = max(1, _env_int("WORKERS", 2))


def validate_config(require_web: bool = False) -> None:
    required = {
        "API_ID": API_ID,
        "API_HASH": API_HASH,
        "BOT_TOKEN": BOT_TOKEN,
        "OWNER_ID": OWNER_ID,
        "MONGO_URI": MONGO_URI,
    }
    if require_web:
        required.update({
            "SECRET_KEY": SECRET_KEY,
            "FLASK_SECRET_KEY": FLASK_SECRET_KEY,
            "ADMIN_PASSWORD": ADMIN_PASSWORD,
        })
    missing = [key for key, value in required.items() if not value]
    if missing:
        raise ValueError("Missing required environment variables: " + ", ".join(missing))
    if require_web and len(SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must contain at least 32 characters.")
    if require_web and len(FLASK_SECRET_KEY) < 32:
        raise ValueError("FLASK_SECRET_KEY must contain at least 32 characters.")
    if require_web and not ADMIN_PASSWORD:
        raise ValueError("ADMIN_PASSWORD must be configured.")
    parsed = urlparse(WEB_URL)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("WEB_URL must be a valid http(s) URL.")
