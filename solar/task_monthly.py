from .models import SolarDay, SolarMonth
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum


def solar_month():
    now = datetime.now()
    solar_ids = settings.SOLAR.keys()
    for solar_id in solar_ids:
        solar = SolarDay.objects.filter(number_solar=solar_id).first()
        if solar is None:
            continue
        solar_month_total = (SolarDay.objects.filter(number_solar=solar_id, created_at__lte=now,
                                                     created_at__gte=now - timedelta(days=30))
                             .aggregate(total_sum=Sum('total_value')))
        solar_month_sum = SolarMonth.objects.create(number_solar=solar_id,
                                                    total_value=solar_month_total.get('total_sum', 0), status=0,
                                                    name=solar.name)
        solar_month_sum.save()


def task_solar_month():
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    scheduler = BackgroundScheduler()
    scheduler.add_job(solar_month, CronTrigger(day='1', hour='0', minute='0'))  # Run at the start of every hour
    scheduler.start()
