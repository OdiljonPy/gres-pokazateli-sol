import requests
from contextlib import suppress
from collections import defaultdict
from datetime import datetime, timedelta
from ..exceptions import BadRequestException
from django.conf import settings

from ..serializers import ReadOnlySolarDAYSerializer

SOLAR = settings.SOLAR


def safe_request(url) -> str:
    response = requests.Response()
    with suppress(Exception):
        response = requests.get(url)
    if response.status_code != 200:
        raise BadRequestException('Bad request or not containing solar data')
    return response.text


def get_data(page, page_size):
    from ..models import SolarDay
    from_ = (page * page_size) - (page_size - 1)
    to_ = page * page_size
    if to_ > len(SOLAR.keys()):
        to_ = len(SOLAR.keys())
    now = datetime.today()
    data = defaultdict(list)
    for i in range(from_, to_ + 1):
        solars = SolarDay.objects.filter(created_at__lte=now - timedelta(hours=6), created_at__gte=now,
                                         number_solar=i).order_by('-created_at')[:12]
        data[f'solar_{i}'] = ReadOnlySolarDAYSerializer(solars, many=True).data
    return {'result': dict(data), 'ok': True}
