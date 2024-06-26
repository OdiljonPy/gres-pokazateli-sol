from .models import SolarDay, SolarHour
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum


def solar_daily():
    now = datetime.now()
    solar_ids = settings.SOLAR.keys()
    for solar_id in solar_ids:
        solar = SolarHour.objects.filter(number_solar=solar_id).first()
        if solar is None:
            continue
        solar_daily_total = (SolarHour.objects.filter(number_solar=solar_id, created_at__lte=now,
                                                      created_at__gte=now - timedelta(days=1))
                             .aggregate(total_sum=Sum('total_value')))
        solar_day_sum = SolarDay.objects.create(number_solar=solar_id,
                                                total_value=solar_daily_total.get('total_sum', 0),
                                                status=0,
                                                name=solar.name)
        solar_day_sum.save()


def task_solar_daily():
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    scheduler = BackgroundScheduler()
    scheduler.add_job(solar_daily, CronTrigger(hour='0', minute='0'))  # Run at the start of every hour
    scheduler.start()
