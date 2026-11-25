from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery
from config import WEB_URL, START_PHOTO, START_CAPTION, OWNER_USERNAME
from database.users import add_user
from database.settings import get_settings
from database.premium import is_premium
from middleware.force_sub import check_force
from middleware.rate_limit import check_rate_limit


def _start_keyboard(settings):
    rows = []
    if WEB_URL.startswith("https://"):
        label = settings.get("webapp_button_text") or "🌐 Open File Store"
        rows.append([InlineKeyboardButton(label[:32], web_app=WebAppInfo(url=WEB_URL))])
    custom = settings.get("custom_buttons") or []
    for index in range(0, min(len(custom), 5), 2):
        pair = custom[index:index + 2]
        rows.append([InlineKeyboardButton(item["text"][:32], url=item["url"]) for item in pair])
    rows.append([InlineKeyboardButton("ℹ️ About", callback_data="about_bot"), InlineKeyboardButton("✖ Close", callback_data="close_msg")])
    return InlineKeyboardMarkup(rows)


def _welcome(user, settings):
    template = settings.get("start_caption") or START_CAPTION
    try:
        caption = template.format(first=user.first_name or "there")
    except (KeyError, ValueError):
        caption = template
    return f"🚀 **{caption}**\n\n📁 Save and retrieve your Telegram files\n🔐 Protected access\n💎 Premium features where enabled"


async def _edit(query, text, keyboard):
    if query.message.photo:
        await query.message.edit_caption(text, reply_markup=keyboard)
    else:
        await query.message.edit_text(text, reply_markup=keyboard)


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
    settings = await get_settings()
    caption, keyboard = _welcome(user, settings), _start_keyboard(settings)
    if START_PHOTO:
        try:
            await message.reply_photo(START_PHOTO, caption=caption, reply_markup=keyboard)
            return
        except Exception:
            pass
    await message.reply_text(caption, reply_markup=keyboard)


@Client.on_message(filters.command("profile") & filters.private)
async def profile_handler(client, message):
    if not message.from_user:
        return
    await add_user(message.from_user.id)
    premium = await is_premium(message.from_user.id)
    status = "Active" if premium else "Free"
    await message.reply_text(f"👤 **Your Profile**\n\n🆔 ID: {message.from_user.id}\n💎 Plan: {status}")


@Client.on_message(filters.command("premium") & filters.private)
async def premium_status_handler(client, message):
    premium = await is_premium(message.from_user.id)
    await message.reply_text("💎 Your premium membership is active." if premium else "You are using the free plan. Contact the bot owner for premium access.")


@Client.on_callback_query(filters.regex("^about_bot$"))
async def about_callback(client, query: CallbackQuery):
    await query.answer()
    settings = await get_settings()
    owner = f"@{OWNER_USERNAME}" if OWNER_USERNAME else "Bot owner"
    about = settings.get("about_text") or "Ultra File Store Pro stores and shares Telegram files using secure expiring links."
    await _edit(query, f"🤖 **Ultra File Store Pro**\n\n{about}\n\nOwner: {owner}", InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_start")]]))


@Client.on_callback_query(filters.regex("^back_start$"))
async def back_to_start(client, query: CallbackQuery):
    await query.answer()
    settings = await get_settings()
    await _edit(query, _welcome(query.from_user, settings), _start_keyboard(settings))


@Client.on_callback_query(filters.regex("^close_msg$"))
async def close_message(client, query: CallbackQuery):
    await query.answer()
    await query.message.delete()
