from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


def task_hourly():
    print("START")
    from .repo.crate_hourly import crate_hourly_solar
    scheduler = BackgroundScheduler()
    scheduler.add_job(crate_hourly_solar, CronTrigger(minute='*'))  # Run at the start of every hour
    scheduler.start()

    # print(scheduler.print_jobs())
    # remove_duplicate_jobs(scheduler, scheduler.get_jobs())
    print(scheduler.get_jobs())

    # print(scheduler.)
    print("END")

#
# def remove_duplicate_jobs(scheduler, jobs):
#     d = {}
#     for job in jobs:
#         if d.get(job.name) is None:
#             d[job.name] = d.get(job.id)
#         else:
#             scheduler.remove_job(job.id)
