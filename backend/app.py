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
    flask_app.config["SECRET_KEY"] = "24f3000060"
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ppa.db"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    flask_app.config["JWT_SECRET_KEY"] = "jwt-secret-key"
    flask_app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  
    flask_app.config["UPLOAD_FOLDER"] = "uploads"
    os.makedirs(flask_app.config["UPLOAD_FOLDER"], exist_ok=True)
    flask_app.config["MAIL_SERVER"] = "localhost"
    flask_app.config["MAIL_PORT"] = 1025
    flask_app.config["MAIL_USE_TLS"] = False
    flask_app.config["MAIL_USE_SSL"] = False
    flask_app.config["MAIL_USERNAME"] = None
    flask_app.config["MAIL_PASSWORD"] = None
    flask_app.config["MAIL_DEFAULT_SENDER"] = ("PPA", "noreply@ppa.com")
    
    CORS(flask_app, resources={r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
        "expose_headers": ["Content-Type", "Authorization"],
        "max_age": 3600
    }})

    try:
        r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        r.ping()
        flask_app.config["CACHE_TYPE"] = "redis"
        flask_app.config["CACHE_REDIS_HOST"] = "localhost"
        flask_app.config["CACHE_REDIS_PORT"] = 6379
        flask_app.config["CACHE_REDIS_DB"] = 0
        flask_app.config["CACHE_DEFAULT_TIMEOUT"] = 300
        flask_app.logger.info("Using Redis cache")
    except Exception as e:
        flask_app.config["CACHE_TYPE"] = "simple"
        flask_app.config["CACHE_DEFAULT_TIMEOUT"] = 300
        flask_app.logger.info(f"Redis not available, using SimpleCache: {e}")
    
    broker_url = "redis://localhost:6379/1"
    result_backend = "redis://localhost:6379/1"
    
    celery.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
    )
    flask_app.config["CELERY_BROKER_URL"] = broker_url
    flask_app.config["CELERY_RESULT_BACKEND"] = result_backend
    
    db.init_app(flask_app)
    jwt.init_app(flask_app)
    mail.init_app(flask_app)
    cache.init_app(flask_app)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            global _flask_app
            if _flask_app:
                with _flask_app.app_context():
                    return self.run(*args, **kwargs)
            else:
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    
    global _flask_app
    _flask_app = flask_app
    
    with flask_app.app_context():
        db.create_all()
        try:
            if not User.query.filter_by(role="admin").first():
                admin_email = "admin@ppa.com"
                admin_password = "admin123"
                hashed = generate_password_hash(admin_password, method="pbkdf2:sha256")
                admin = User(username="admin", email=admin_email, password_hash=hashed, role="admin")
                db.session.add(admin)
                db.session.commit()
                flask_app.logger.info(f"Admin user '{admin_email}' created.")
            else:
                flask_app.logger.info("Admin user already exists.")
        except Exception as e:
            flask_app.logger.error(f"Error creating admin user: {e}")
            db.session.rollback()
    
    from routes import register_routes
    register_routes(flask_app, db, jwt, mail, cache, celery)
    
    from tasks import register_tasks
    register_tasks(celery, mail)

    return flask_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)