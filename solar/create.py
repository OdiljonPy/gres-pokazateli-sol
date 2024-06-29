from django.conf import settings
from datetime import timedelta
from django.db.models import Avg, Sum
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


def create_hourly_solar():
    print('soatlik')
    from .models import SolarHour, Solar
    now = timezone.now()
    solars = settings.SOLAR.keys()
    for i in solars:
        solar = Solar.objects.filter(number_solar=i).first()
        if solar is None:
            continue
        solar_avg = Solar.objects.filter(
            number_solar=i,
            created_at__lte=now,
            created_at__gte=now - timedelta(hours=1)
        ).aggregate(total_avg=Avg('value'))
        total_value = solar_avg.get('total_avg') or 0
        solar_hour = SolarHour.objects.create(
            number_solar=i,
            name=solar.name,
            total_value=round(total_value, 1),
            status=0
        )
        solar_hour.save()


def create_daily_solar():
    print('kunlik')
    from .models import SolarHour, SolarDay
    now = timezone.now()
    solars = settings.SOLAR.keys()
    for i in solars:
        solar = SolarHour.objects.filter(number_solar=i).first()
        if solar is None:
            continue
        solar_sum = SolarHour.objects.filter(
            number_solar=i,
            created_at__lte=now,
            created_at__gte=now - timedelta(days=1)
        ).aggregate(total_sum=Sum('total_value'))
        total_value = solar_sum.get('total_sum') or 0
        solar_day = SolarDay.objects.create(
            number_solar=i,
            name=solar.name,
            total_value=round(total_value, 1),
            status=0
        )
        solar_day.save()


def solar_month():
    print('oylik')
    from .models import SolarDay, SolarMonth
    previous_month = timezone.now().month
    previous_year_ = timezone.now().year
    solar_ids = settings.SOLAR.keys()
    for solar_id in solar_ids:
        solar = SolarDay.objects.filter(number_solar=solar_id).first()
        if solar is None:
            continue
        solar_month_total = SolarDay.objects.filter(
            number_solar=solar_id,
            created_at__month=previous_month,
            created_at__year=previous_year_
        ).aggregate(total_sum=Sum('total_value'))
        total_value = solar_month_total.get('total_sum') or 0
        solar_month_sum = SolarMonth.objects.create(
            number_solar=solar_id,
            total_value=round(total_value, 1),
            status=0,
            name=solar.name
        )
        solar_month_sum.save()


def solar_yearly():
    print('yillik')
    from .models import SolarMonth, SolarYear
    previous_year_ = timezone.now().year
    solar_ids = settings.SOLAR.keys()
    for solar_id in solar_ids:
        solar = SolarMonth.objects.filter(number_solar=solar_id).first()
        if solar is None:
            continue
        solar_yearly_total = SolarMonth.objects.filter(
            number_solar=solar_id,
            created_at__year=previous_year_
        ).aggregate(total_sum=Sum('total_value'))
        total_value = solar_yearly_total.get('total_sum') or 0
        solar_year_sum = SolarYear.objects.create(
            number_solar=solar_id,
            total_value=round(total_value, 1),
            status=0,
            name=solar.name
        )
        solar_year_sum.save()


def create_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(create_hourly_solar, trigger='cron', minute=59, timezone='UTC')
    scheduler.add_job(create_daily_solar, trigger='cron', hour=23, minute=58, timezone='UTC')
    trigger = CronTrigger(day='last', hour=23, minute=58, timezone='UTC')
    scheduler.add_job(solar_month, trigger=trigger)
    scheduler.add_job(solar_yearly, trigger='cron', month=12, day=31, hour=23, minute=58, timezone='UTC')
    scheduler.start()
    for i in scheduler.get_jobs():
        print(i)
