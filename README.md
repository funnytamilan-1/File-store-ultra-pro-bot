# Ultra File Store Pro Bot

A Python Telegram file-store bot with a MongoDB database and a Flask admin dashboard. This setup matches the current repository source tree.

## Included in this branch

- Pyrogram bot with /start and /profile
- MongoDB user, file, admin, premium and activity-log records
- Multiple force-subscribe channels configured from the web panel
- Admin-only text and replied-message broadcasts
- Owner-managed Telegram bot admins
- Premium add/remove commands with expiry handling
- Signed file-download links (24-hour link expiry)
- Optional file-record expiry using AUTO_DELETE_HOURS
- Flask admin dashboard for users, files, admins, premium records, settings, broadcasts and logs
- CSRF-protected admin forms and secure session cookie defaults
- Docker image and GitHub Actions syntax/tests

## Requirements

- Python 3.11+
- MongoDB (Atlas or self-hosted)
- Telegram bot token from https://t.me/BotFather
- Telegram API ID and API hash from https://my.telegram.org

## Configure

Copy .env.example to .env and fill in real values. Never commit .env.

~~~bash
cp .env.example .env
~~~

Generate independent secrets:

~~~bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
~~~

Set SECRET_KEY and FLASK_SECRET_KEY to separate generated values. Set a long unique ADMIN_PASSWORD. WEB_URL must be your public HTTPS URL for Telegram Web App buttons and download links.

## Run locally

~~~bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
~~~

Start the Telegram bot:

~~~bash
python bot.py
~~~

In a second terminal, start the admin web app:

~~~bash
gunicorn --workers 2 --bind 0.0.0.0:8000 wsgi:app
~~~

Open http://localhost:8000/login for local testing. In production, use HTTPS and set DEBUG=false.

## Docker

Build and run after creating .env:

~~~bash
docker build -t ultra-file-store .
docker run --env-file .env -p 8000:8000 ultra-file-store
~~~

For production, use a process supervisor or separate bot and web services so either process can restart independently. Keep MongoDB persistent and back it up regularly.

## Bot commands

| Command | Access | Purpose |
|---|---|---|
| /start | Everyone | Start bot and check required channels |
| /profile | Everyone | Show Telegram user ID |
| /stats | Admin | View bot totals |
| /broadcast text | Admin | Send a text broadcast |
| Reply + /broadcast | Admin | Copy a message to users |
| /addadmin user_id | Owner | Add an admin |
| /removeadmin user_id | Owner | Remove an admin |
| /addpremium user_id days | Admin | Grant premium time |
| /delpremium user_id | Admin | Remove premium |

## Force subscribe

Open Force Subscribe in the admin panel and enter one channel username or numeric channel ID per line. The bot must be an administrator in each required channel so it can check membership. A channel ID is recommended for private channels.

## File links and expiry

When a user sends a document, video or audio file to the bot, the bot stores its Telegram file reference and returns a signed download link. Links expire after 24 hours.

AUTO_DELETE_HOURS=0 keeps file records until manually removed. A positive value causes the database record (and therefore this app's download link) to expire after that many hours. It does not delete the original Telegram message or Telegram's stored media.

## Security notes

- Keep .env, bot tokens, MongoDB credentials and generated secrets private.
- Use a unique long admin password and HTTPS.
- Give the bot only the Telegram channel permissions it needs.
- Broadcast only to users who have started the bot; Telegram may reject delivery to users who blocked it.
- Signed links control access through this web app; they do not prevent a recipient from sharing a downloaded copy.

## Current limitations / follow-up work

A URL-shortener provider is not hard-coded because each provider uses a different API contract; connect one only after its API documentation and credentials are supplied. The current project also does not implement Telegram-side message deletion, custom per-user button/message editing, or content DRM. These should not be advertised as active features until implemented and tested.

## Development checks

~~~bash
python -m compileall -q .
pytest -q
~~~
