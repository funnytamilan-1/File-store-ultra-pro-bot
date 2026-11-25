 # Ultra File Store Pro Bot

A Python Telegram file-store bot with MongoDB and a Flask admin dashboard.

## Included

- Pyrogram bot with /start and /profile
- MongoDB user, file, admin, premium and activity-log records
- Multiple force-subscribe channels managed from the dashboard
- Admin-only text and replied-message broadcasts
- Owner-managed bot admins; delegated admins can sign in through Telegram Web App initData
- Premium add/remove commands with expiry handling
- HMAC-signed file-download links (24-hour link expiry)
- Optional file-record expiry with AUTO_DELETE_HOURS
- Flask dashboard for users, files, admins, premium, settings, broadcasts and logs
- CSRF-protected forms, secure session cookies, Docker and CI checks

## Requirements

- Python 3.11+
- MongoDB Atlas or self-hosted MongoDB
- Telegram bot token from https://t.me/BotFather
- Telegram API ID/hash from https://my.telegram.org

## Configure

Copy .env.example to .env and fill the values. Do not commit .env. Generate independent secrets with:

~~~bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
~~~

Set SECRET_KEY and FLASK_SECRET_KEY to different generated values. Set a long unique ADMIN_PASSWORD. WEB_URL must be your public HTTPS URL for Telegram Web Apps and download links. Configure the domain for Telegram Web Apps with BotFather before using initData login.

## Local run

~~~bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python bot.py
~~~

In a second terminal:

~~~bash
gunicorn --workers 2 --bind 0.0.0.0:8000 wsgi:app
~~~

Open http://localhost:8000/login for local owner-password testing. A delegated bot admin should open the panel from the Telegram Web App button. In production, use HTTPS.

## Docker

~~~bash
docker build -t ultra-file-store .
docker run --env-file .env -p 8000:8000 ultra-file-store
~~~

For production, separate the bot and web processes or use a process supervisor so either can restart independently. Use persistent MongoDB and regular backups.

## Bot commands

| Command | Access | Purpose |
|---|---|---|
| /start | Everyone | Start and check required channels |
| /profile | Everyone | Show Telegram user ID |
| /stats | Admin | View totals |
| /broadcast text | Admin | Send text to registered users |
| Reply + /broadcast | Admin | Copy a message to registered users |
| /addadmin user_id | Owner | Add bot admin |
| /removeadmin user_id | Owner | Remove bot admin |
| /addpremium user_id days | Admin | Grant premium time |
| /delpremium user_id | Admin | Remove premium |

## Force subscribe

In the dashboard, enter one channel username or numeric channel ID per line. The bot must be an administrator in every required channel so it can check membership.

## File links and expiry

Sending a document, video or audio file to the bot stores its Telegram file reference and returns a signed download link. The link expires after 24 hours. AUTO_DELETE_HOURS=0 keeps the database record; a positive value expires the database record and disables this app's download link after that many hours. It does not delete the original Telegram message or Telegram's stored media.

## Security and limitations

- Keep .env, bot tokens, MongoDB credentials and secrets private.
- Use HTTPS and a unique admin password.
- Telegram Web App admin sign-in validates initData and checks the user against the admins collection.
- Signed links protect this app's download endpoint; they cannot prevent recipients sharing a downloaded copy.
- A URL shortener is not connected because the repository does not specify a provider API. Custom per-user messages/buttons and Telegram-side message deletion also remain follow-up work; they are not advertised as implemented.

## Checks

~~~bash
python -m compileall -q .
pytest -q
~~~
