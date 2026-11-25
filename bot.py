from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, validate_config

validate_config()

app = Client(
    "FileStoreBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "plugins"},
)


if __name__ == "__main__":
    app.run()
