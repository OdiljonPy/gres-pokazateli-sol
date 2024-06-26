from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .repo.crate_hourly import crate_hourly_solar


def task_hourly():
    scheduler = BackgroundScheduler()
    scheduler.add_job(crate_hourly_solar, CronTrigger(minute='0'))  # Run at the start of every hour
    scheduler.start()
