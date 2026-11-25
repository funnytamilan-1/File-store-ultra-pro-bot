import asyncio
import os
import tempfile
from pathlib import Path
from flask import render_template, request, redirect, session, url_for, flash, send_file, abort
from werkzeug.security import check_password_hash
from pyrogram import Client
from config import ADMIN_PASSWORD, API_ID, API_HASH, BOT_TOKEN, OWNER_ID, SECRET_KEY
from web import web
from web.auth import login_required
from database.users import count_users, get_all_users
from database.admins import add_admin, remove_admin, get_all_admins, is_admin
from database.files import count_files, get_file
from database.premium import get_all_premium
from database.settings import get_settings, update_settings
from database.logs import get_logs, add_log
from utils.link_generator import verify_secure_link
from utils.webapp_verify import get_verified_webapp_user


def _valid_admin_password(value: str) -> bool:
    if not ADMIN_PASSWORD:
        return False
    if ADMIN_PASSWORD.startswith(("pbkdf2:", "scrypt:")):
        try:
            return check_password_hash(ADMIN_PASSWORD, value or "")
        except ValueError:
            return False
    import hmac
    return hmac.compare_digest(ADMIN_PASSWORD, value or "")


def _new_bot_client():
    return Client("filestore_web_worker", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)


@web.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "POST":
        init_data = request.form.get("init_data", "")
        web_user = get_verified_webapp_user(init_data) if init_data else None
        if web_user and await is_admin(int(web_user["id"])):
            session.clear()
            session["admin_authenticated"] = True
            session["admin_user_id"] = int(web_user["id"])
            session.permanent = True
            return redirect(request.args.get("next") or url_for("web.dashboard"))
        if _valid_admin_password(request.form.get("password", "")):
            session.clear()
            session["admin_authenticated"] = True
            session["admin_user_id"] = OWNER_ID
            session.permanent = True
            return redirect(request.args.get("next") or url_for("web.dashboard"))
        flash("Invalid password or Telegram admin account.", "error")
    return render_template("login.html")


@web.route("/logout", methods=["POST"])
async def logout():
    session.clear()
    return redirect(url_for("web.login"))


@web.route("/")
@login_required
async def dashboard():
    users, files, settings = await asyncio.gather(count_users(), count_files(), get_settings())
    return render_template("dashboard.html", users=users, files=files, settings=settings)


@web.route("/admins", methods=["GET", "POST"])
@login_required
async def admins():
    if int(session.get("admin_user_id", 0)) != OWNER_ID:
        abort(403)
    if request.method == "POST":
        try:
            user_id = int(request.form.get("user_id", ""))
        except ValueError:
            flash("Enter a valid Telegram user ID.", "error")
            return redirect(url_for("web.admins"))
        action = request.form.get("action")
        if action == "add":
            await add_admin(user_id)
        elif action == "remove":
            if user_id == OWNER_ID:
                flash("The owner account cannot be removed.", "error")
            else:
                await remove_admin(user_id)
        return redirect(url_for("web.admins"))
    cursor = await get_all_admins()
    admins_list = await cursor.to_list(length=200)
    if not any(item.get("user_id") == OWNER_ID for item in admins_list):
        admins_list.insert(0, {"user_id": OWNER_ID})
    return render_template("admins.html", admins=admins_list, config_owner_id=OWNER_ID)


@web.route("/users")
@login_required
async def users_page():
    cursor = await get_all_users()
    users = await cursor.to_list(length=200)
    return render_template("users.html", users=users)


@web.route("/premium")
@login_required
async def premium_page():
    cursor = await get_all_premium()
    premium = await cursor.to_list(length=200)
    return render_template("premium.html", premium=premium)


@web.route("/settings", methods=["GET", "POST"])
@login_required
async def settings_page():
    if request.method == "POST":
        channels = [value.strip() for value in request.form.get("force_channels", "").splitlines() if value.strip()]
        await update_settings({"force_channels": channels, "force_channel": channels[0] if channels else None, "force_join_request": bool(request.form.get("force_join"))})
        flash("Settings saved.", "success")
        return redirect(url_for("web.settings_page"))
    settings = await get_settings()
    settings["force_channels_text"] = "\n".join(settings.get("force_channels") or ([settings["force_channel"]] if settings.get("force_channel") else []))
    return render_template("settings.html", settings=settings)


@web.route("/broadcast", methods=["GET", "POST"])
@login_required
async def broadcast_page():
    if request.method == "POST":
        text = request.form.get("message", "").strip()
        if not text:
            flash("Broadcast message cannot be empty.", "error")
            return redirect(url_for("web.broadcast_page"))
        sent = failed = 0
        cursor = await get_all_users()
        bot = _new_bot_client()
        try:
            await bot.start()
            async for user in cursor:
                try:
                    await bot.send_message(int(user["user_id"]), text)
                    sent += 1
                except Exception:
                    failed += 1
        finally:
            if bot.is_connected:
                await bot.stop()
        await add_log("web_broadcast", user_id=int(session.get("admin_user_id", OWNER_ID)), extra={"sent": sent, "failed": failed})
        flash(f"Broadcast finished. Delivered: {sent}; failed: {failed}.", "success")
        return redirect(url_for("web.broadcast_page"))
    return render_template("broadcast.html")


@web.route("/logs")
@login_required
async def logs_page():
    cursor = await get_logs(100)
    logs = await cursor.to_list(length=100)
    return render_template("logs.html", logs=logs)


@web.route("/file/<file_id>")
async def stream_file(file_id):
    if not SECRET_KEY:
        abort(503, "Secure file links are not configured.")
    exp, sig = request.args.get("exp", type=int), request.args.get("sig", "")
    if not exp or not verify_secure_link(file_id, exp, sig):
        abort(403, "This file link is invalid or expired.")
    record = await get_file(file_id)
    if not record:
        abort(404, "File not found.")
    suffix = Path(record.get("file_name") or "download.bin").suffix
    fd, temp_path = tempfile.mkstemp(prefix="filestore_", suffix=suffix)
    os.close(fd)
    bot = _new_bot_client()
    try:
        await bot.start()
        downloaded = await bot.download_media(file_id, file_name=temp_path)
        if not downloaded:
            raise RuntimeError("Telegram returned no downloaded file.")
    except Exception:
        try:
            os.remove(temp_path)
        except OSError:
            pass
        abort(502, "Unable to retrieve this file from Telegram.")
    finally:
        if bot.is_connected:
            await bot.stop()
    response = send_file(downloaded, as_attachment=True, download_name=record.get("file_name") or "download.bin")
    response.call_on_close(lambda: os.path.exists(temp_path) and os.remove(temp_path))
    return response
