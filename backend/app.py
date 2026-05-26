import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_caching import Cache
from celery import Celery
from celery.schedules import crontab
import redis
from werkzeug.security import generate_password_hash
from models import db, User

_flask_app = None
celery = Celery('ppa')
jwt = JWTManager()
mail = Mail()
cache = Cache()

celery.conf.update(
    broker_url="redis://localhost:6379/1",
    result_backend="redis://localhost:6379/1",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "send-monthly-placement-report": {
            "task": "send_monthly_placement_report",
            "schedule": crontab(day_of_month=1, hour=0, minute=0),  
        },
        "send-daily-visit-reminders": {
            "task": "send_visit_reminders",
            "schedule": crontab(hour=9, minute=0),  
        },
    },
)


def create_app():
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = "super-secret-key"
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ppa.db"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["JWT_SECRET_KEY"] = "jwt-secret-key"
    
    flask_app.config["MAIL_SERVER"] = "localhost"
    flask_app.config["MAIL_PORT"] = 1025
    flask_app.config["MAIL_USE_TLS"] = False
    flask_app.config["MAIL_USE_SSL"] = False
    flask_app.config["MAIL_USERNAME"] = None
    flask_app.config["MAIL_PASSWORD"] = None
    flask_app.config["MAIL_DEFAULT_SENDER"] = ("PPA", "noreply@ppa.local")
    
    CORS(flask_app, resources={r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "expose_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }})
    
    global _flask_app
    _flask_app = flask_app
    
    return flask_app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)