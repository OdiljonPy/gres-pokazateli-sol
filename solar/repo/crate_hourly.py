from ..models import Solar
from ..models import SolarHour
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Avg


def crate_hourly_solar():
    now = datetime.now()
    solar = settings.SOLAR.keys()
    for i in solar:
        solar = Solar.objects.filter(number_solar=i).first()
        solar_avg = Solar.objects.filter(number_solar=i, created_at__lte=now,
                                         created_at__gte=now - timedelta(hours=1)).aggregate(total_avg=Avg('value'))
        solar_hour = SolarHour.objects.create(number_solar=i, name=solar.name, key=solar.key,
                                              total_value=solar_avg['total_avg'])
        solar_hour.save()
