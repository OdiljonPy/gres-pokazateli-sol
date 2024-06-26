from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


def task_hourly():
    from .repo.crate_hourly import crate_hourly_solar
    scheduler = BackgroundScheduler()
    scheduler.add_job(crate_hourly_solar, CronTrigger(minute='27'))  # Run at the start of every hour
    scheduler.start()
# scheduler = None  # Initialize scheduler as None
#
#
# def task_hourly():
#     global scheduler
#     if scheduler is None:
#         from .repo.crate_hourly import crate_hourly_solar
#         scheduler = BackgroundScheduler()
#         scheduler.add_job(crate_hourly_solar, CronTrigger(minute='36'))  # Run at the 27th minute of every hour
#         scheduler.start()
