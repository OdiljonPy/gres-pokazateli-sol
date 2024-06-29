from collections import defaultdict
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from ..serializers import ReadOnlySolarDAYSerializer

SOLAR = settings.SOLAR


def get_data(page, page_size):
    from ..models import SolarHour
    from_ = (page * page_size) - (page_size - 1)
    to_ = page * page_size
    if to_ > len(SOLAR.keys()):
        to_ = len(SOLAR.keys())
    now = timezone.now()
    data = defaultdict(list)
    for i in range(from_, to_ + 1):
        solars = SolarHour.objects.filter(created_at__lte=now, created_at__gte=now - timedelta(hours=6),
                                          number_solar=i).order_by('-created_at')[:12]
        print(solars)
        data[f'solar_{i}'] = ReadOnlySolarDAYSerializer(solars, many=True).data
    return {'result': dict(data), 'ok': True}
