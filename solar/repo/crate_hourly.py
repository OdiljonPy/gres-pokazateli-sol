from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Avg


def crate_hourly_solar():
    print("TASK BOSHLANDI")
    from ..models import Solar
    from ..models import SolarHour
    now = datetime.now()
    solars = settings.SOLAR.keys()
    print(now)
    print(solars)
    for i in solars:
        solar = Solar.objects.filter(number_solar=i).first()
        print(solar)
        if solar is None:
            continue
        print(Solar.objects.filter(number_solar=i))
        solar_avg = Solar.objects.filter(number_solar=i, created_at__lte=now,
                                         created_at__gte=now - timedelta(hours=1)).aggregate(total_avg=Avg('value'))
        print(solar_avg)
        solar_hour = SolarHour.objects.create(number_solar=i, name=solar.name,
                                              total_value=solar_avg('total_avg', 0), status=0)
        print(solar_hour)
        solar_hour.save()
    print("TASK TUGADI")
