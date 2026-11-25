from functools import wraps
from flask import session, redirect, request, url_for


def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("web.login", next=request.path))
        return await func(*args, **kwargs)
    return wrapper
