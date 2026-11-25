from flask import Flask
from web.routes import web
from config import PORT, FLASK_SECRET_KEY, DEBUG

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY or None
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=not DEBUG,
    PERMANENT_SESSION_LIFETIME=60 * 60 * 8,
)
app.register_blueprint(web)


@app.get("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
