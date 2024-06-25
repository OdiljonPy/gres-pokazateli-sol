import requests
from contextlib import suppress
from collections import defaultdict
from datetime import datetime, timedelta
from ..exceptions import BadRequestException
from django.conf import settings
from django.utils import timezone

SOLAR = settings.SOLAR


def safe_request(url) -> str:
    response = requests.Response()
    with suppress(Exception):
        response = requests.get(url)
    if response.status_code != 200:
        raise BadRequestException('Bad request or not containing solar data')
    return response.text


def get_data(page, page_size):
    from_ = (page * page_size) - (page_size - 1)
    to_ = page * page_size
    if to_ > len(SOLAR.keys()):
        to_ = len(SOLAR.keys())
    now = datetime.today()
    # now = timezone.now().today()
    six_hours_before = now - timedelta(hours=11)
    year = six_hours_before.year
    month = six_hours_before.month if six_hours_before.month > 9 else f"0{six_hours_before.month}"
    day = six_hours_before.day if six_hours_before.day > 9 else f"0{six_hours_before.day}"
    hour = six_hours_before.hour if six_hours_before.hour > 9 else f"0{six_hours_before.hour}"
    real_rows = safe_request(
        url=f"http://195.69.218.121/crq?req=archive&type=g&interval=main&"
            f"t1={year}{month}{day}{hour}0000"
    )

    data = defaultdict(list)
    for j in range(from_, to_ + 1):
        solar_data = list(
            filter(lambda row: row.split(',')[0] == SOLAR.get(j).get('P_total'), real_rows.split('\n')[2:]))
        for row_ in solar_data:
            time = row_.split(',')[1].strip().replace('w', '')
            formatted_created_at = datetime.strptime(time, '%d-%m-%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            data[f"solar_{j}"].append(
                {
                    "value": round(float(row_.split(',')[2]), 2),
                    "created_at": formatted_created_at,
                }
            )

    return {'result': dict(data), 'ok': True}
