from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery
from config import WEB_URL, START_PHOTO, START_CAPTION, OWNER_USERNAME
from database.users import add_user
from middleware.force_sub import check_force
from middleware.rate_limit import check_rate_limit


def _start_keyboard():
    rows = []
    if WEB_URL.startswith("https://"):
        rows.append([InlineKeyboardButton("🌐 Open File Store", web_app=WebAppInfo(url=WEB_URL))])
    rows.append([InlineKeyboardButton("ℹ️ About", callback_data="about_bot"), InlineKeyboardButton("✖ Close", callback_data="close_msg")])
    return InlineKeyboardMarkup(rows)


def _welcome(user):
    try:
        caption = START_CAPTION.format(first=user.first_name or "there")
    except (KeyError, ValueError):
        caption = START_CAPTION
    return f"🚀 **{caption}**\n\n📁 Save and retrieve your Telegram files\n🔐 Protected access\n💎 Premium features where enabled"


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user = message.from_user
    if not user:
        return
    if not await check_rate_limit(user.id):
        await message.reply_text("Please wait a few seconds before trying again.")
        return
    await add_user(user.id)
    if not await check_force(client, user.id):
        await message.reply_text("🚫 Please join all required channels, then send /start again.")
        return
    caption, keyboard = _welcome(user), _start_keyboard()
    if START_PHOTO:
        try:
            await message.reply_photo(START_PHOTO, caption=caption, reply_markup=keyboard)
            return
        except Exception:
            pass
    await message.reply_text(caption, reply_markup=keyboard)


@Client.on_message(filters.command("profile") & filters.private)
async def profile_handler(client, message):
    if message.from_user:
        await add_user(message.from_user.id)
        await message.reply_text(f"👤 **Your Profile**\n\n🆔 ID: {message.from_user.id}")


@Client.on_callback_query(filters.regex("^about_bot$"))
async def about_callback(client, query: CallbackQuery):
    await query.answer()
    owner = f"@{OWNER_USERNAME}" if OWNER_USERNAME else "Bot owner"
    await query.message.edit_caption(
        f"🤖 **Ultra File Store Pro**\n\nOwner: {owner}\nBuilt with Pyrogram, Flask and MongoDB.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_start")]])
    )


@Client.on_callback_query(filters.regex("^back_start$"))
async def back_to_start(client, query: CallbackQuery):
    await query.answer()
    await query.message.edit_caption(_welcome(query.from_user), reply_markup=_start_keyboard())


@Client.on_callback_query(filters.regex("^close_msg$"))
async def close_message(client, query: CallbackQuery):
    await query.answer()
    await query.message.delete()
