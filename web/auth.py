from functools import wraps
from flask import session, redirect, request, url_for
from database.admins import is_admin


def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user_id = session.get("admin_user_id")
        if not session.get("admin_authenticated") or not user_id or not await is_admin(int(user_id)):
            session.clear()
            return redirect(url_for("web.login", next=request.path))
        return await func(*args, **kwargs)
    return wrapper
