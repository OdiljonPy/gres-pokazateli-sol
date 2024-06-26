from .models import SolarDay, SolarMonth
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum


def task_solar_month():
    now = datetime.now()
    solar_ids = settings.SOLAR.keys()
    for solar_id in solar_ids:
        solar_month_total = (SolarDay.objects.filter(number_solar=solar_id, created_at__lte=now,
                                                     created_at__gte=now - timedelta(days=30))
                             .aggregate(total_sum=Sum('total_value')))
        solar_month = SolarMonth.objects.create(number_solar=solar_id, total_value=solar_month_total, status=0,
                                              name=str(solar_id))
        solar_month.save()