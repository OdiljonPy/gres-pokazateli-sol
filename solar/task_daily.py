from .models import SolarDay, SolarHour
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum


def task_solar_daily():
    now = datetime.now()
    solar_ids = settings.SOLAR.keys()
    for solar_id in solar_ids:
        solar_daily_total = (SolarHour.objects.filter(number_solar=solar_id, created_at__lte=now,
                                                      created_at__gte=now - timedelta(days=1))
                             .aggregate(total_sum=Sum('total_value')))
        solar_day = SolarDay.objects.create(number_solar=solar_id, total_value=solar_daily_total, status=0, name=str(solar_id))
