from celery import Celery, Task
from backend.config import config_settings
from flask import Flask
from celery.schedules import crontab


class CeleryConfig:
    broker_url = "redis://localhost:6379/0"
    result_backend = "redis://localhost:6379/1"
    beat_schedule = {
        "send-daily-reminders after 60": {
            "task": "backend.tasks.greeting_task",
            "schedule": 7200.0,  # for testing, after 2 hours
        },
        "daily-user-reminder-at-6pm": {
            "task": "backend.tasks.email_for_daily_reminders",
            "schedule": crontab(hour=18, minute=00),  # 6 PM IST daily
            "args": (),
        },
        "monthly-report-generation": {
            "task": "backend.tasks.generate_monthly_report",
            "schedule": crontab(day_of_month=25, hour=21, minute=49),  # 25th day of every month at 7:20 PM
            "args": (),
        },
        
    }
    timezone = "Asia/Kolkata"
    enable_utc = True
    include = ["backend.tasks"]

def make_celery(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(CeleryConfig)
    celery_app.set_default()
    app.extensions['celery'] = celery_app
    return celery_app
