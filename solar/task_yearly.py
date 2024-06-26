from .models import SolarMonth, SolarYear
from datetime import datetime, timedelta
from django.conf import settings
from django.db.models import Sum


def task_solar_yearly():
    now = datetime.now()
    solar_ids = settings.SOLAR.keys()
    for solar_id in solar_ids:
        solar_yearly_total = (SolarMonth.objects.filter(number_solar=solar_id, created_at__lte=now,
                                                        created_at__gte=now - timedelta(days=365))
                              .aggregate(total_sum=Sum('total_value')))
        solar_year = SolarYear.objects.create(number_solar=solar_id, total_value=solar_yearly_total, status=0,
                                              name=str(solar_id))
