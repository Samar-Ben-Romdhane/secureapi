from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.models.models import db
from src.routes.auth import auth_bp
from src.routes.tasks import tasks_bp
from dotenv import load_dotenv
import os
load_dotenv()
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
    db_url = os.environ.get("DATABASE_URL", "sqlite:////home/samar/secureapi/secureapi.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["100 per hour", "20 per minute"],
        storage_uri="memory://",
    )

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)
