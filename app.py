from flask import Flask
from flask_wtf.csrf import CSRFProtect
from web.routes import web
from config import PORT, FLASK_SECRET_KEY, DEBUG, validate_config

validate_config(require_web=True)

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=not DEBUG,
    PERMANENT_SESSION_LIFETIME=60 * 60 * 8,
)
CSRFProtect(app)
app.register_blueprint(web)


@app.get("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
