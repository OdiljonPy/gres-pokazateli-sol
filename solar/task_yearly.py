from .models import SolarMonth, SolarYear
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum


def solar_yearly():
    now = datetime.now()
    solar_ids = settings.SOLAR.keys()
    for solar_id in solar_ids:
        solar = SolarMonth.objects.filter(number_solar=solar_id).first()
        if solar is None:
            continue
        solar_yearly_total = (SolarMonth.objects.filter(number_solar=solar_id, created_at__lte=now,
                                                        created_at__gte=now - timedelta(days=365))
                              .aggregate(total_sum=Sum('total_value')))
        solar_year_sum = SolarYear.objects.create(number_solar=solar_id,
                                                  total_value=solar_yearly_total.get('total_sum'), status=0,
                                                  name=solar.name)
        solar_year_sum.save()


def task_solar_yearly():
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    scheduler = BackgroundScheduler()
    scheduler.add_job(solar_yearly,
                      CronTrigger(month='1', day='1', hour='0', minute='0'))  # Run at the start of every hour
    scheduler.start()
