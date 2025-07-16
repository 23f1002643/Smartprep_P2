import os
from datetime import timedelta

config_settings = {
    'FLASK_DEBUG': os.getenv('FLASK_DEBUG', True),
    'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URI', 'sqlite:///backend/db.sqlite3'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': os.getenv('SECRET_KEY', 'my_secret_key'),
    'PERMANENT_SESSION_LIFETIME': timedelta(minutes=30),

    # Redis & Celery
    'REDIS_HOST': os.getenv('REDIS_HOST', 'localhost'),
    'REDIS_PORT': 6379,
    'REDIS_DB_CACHE': 0,
    'CACHE_TYPE': 'redis',
    'CELERY_BROKER_URL': os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    'CELERY_RESULT_BACKEND': os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'), 
    'CACHE_REDIS_URL': os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0'),
    'TIMEZONE': 'Asia/Kolkata',

    # JWT
    'JWT_SECRET_KEY': 'jai_shree_ram',
    'JWT_ACCESS_TOKEN_EXPIRES': timedelta(days=1),
    'JWT_BLOCKLIST': set(),


    # Email - MailHog Configuration
    'MAIL_SERVER': 'localhost',
    'MAIL_PORT': int(os.getenv('MAIL_PORT', 1025)),
    'MAIL_USE_TLS': False,
    'MAIL_USE_SSL': False,
    'MAIL_USERNAME': os.getenv('MAIL_USERNAME', None),     
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD', None),      
    'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER', 'Smartprep <admin@quizmaster.com>')
}
