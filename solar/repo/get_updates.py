from contextlib import suppress
from datetime import datetime, timedelta

import requests
from django.conf import settings

from ..exceptions import BadRequestException
from django.db.models import Sum

SOLAR = settings.SOLAR


def safe_request(url) -> str:
    response = requests.Response()
    with suppress(Exception):
        response = requests.get(url)
    if response.status_code != 200:
        raise BadRequestException('Bad request or not containing solar data')
    return response.text


def get_solar_data(channels: dict, rows_: str) -> float:
    ll = list(
        map(
            lambda text_row: float(text_row.split(',')[2]) / 1000 * channels.get(text_row.split(',')[0]),
            list(filter(lambda row: row.split(',')[0] in channels and len(row.split(',')) > 3, rows_.split('\n')[2:]))
        ))
    if ll:
        return sum(ll) / (len(ll) / len(channels))
    return 0


def get_channel_data_for_lifetime() -> dict:
    real_rows = safe_request(
        url="http://10.10.20.1/crq?req=current"
    )
    res = {}
    for row in real_rows.split('\n')[2:]:
        if len(row.split(',')) > 3:
            res[row.split(',')[0]] = float(row.split(',')[2])
    return res


def get_live(page, page_size) -> dict:
    from_ = (page * page_size) - (page_size - 1)
    to_ = page * page_size
    if to_ > len(SOLAR.keys()):
        to_ = len(SOLAR.keys())

    all_channels = get_channel_data_for_lifetime()

    data = list(
        map(lambda i: {
            f'solar_{i}':
                {
                    'P_total': round(
                        (all_channels.get(SOLAR.get(i).get('P_total'), 0.0) / 1000) * SOLAR.get(i).get('coefficient'),
                        2),
                    'P_1': round(
                        (all_channels.get(SOLAR.get(i).get('P_1'), 0.0) / 1000) * SOLAR.get(i).get('coefficient'), 2),
                    'P_2': round(
                        (all_channels.get(SOLAR.get(i).get('P_2'), 0.0) / 1000) * SOLAR.get(i).get('coefficient'), 2),
                    'P_3': round(
                        (all_channels.get(SOLAR.get(i).get('P_3'), 0.0) / 1000) * SOLAR.get(i).get('coefficient'), 2),
                    'U_1': round(all_channels.get(SOLAR.get(i).get('U_1'), 0.0), 2),
                    'U_2': round(all_channels.get(SOLAR.get(i).get('U_2'), 0.0), 2),
                    'U_3': round(all_channels.get(SOLAR.get(i).get('U_3'), 0.0), 2),
                    'I_1': round(
                        (all_channels.get(SOLAR.get(i).get('I_1'), 0.0) / 1000) * SOLAR.get(i).get('coefficient'), 2),
                    'I_2': round(
                        (all_channels.get(SOLAR.get(i).get('I_2'), 0.0) / 1000) * SOLAR.get(i).get('coefficient'), 2),
                    'I_3': round(
                        (all_channels.get(SOLAR.get(i).get('I_3'), 0.0) / 1000) * SOLAR.get(i).get('coefficient'), 2),
                    'f': round(all_channels.get(SOLAR.get(i).get('f'), 0.0), 2),
                    'count': SOLAR.get(i).get('count')
                }
        }, list(range(from_, to_ + 1)))
    )
    # date = get_datetime()
    #
    # P_total_channels = list(
    #     map(lambda i: [SOLAR.get(i).get('P_total'), SOLAR.get(i).get('coefficient')], list(range(from_, to_ + 1)))
    # )
    # P_total_channels = dict(P_total_channels)

    res_data = {}
    for item in data:
        res_data[list(item.keys())[0]] = list(item.values())[0]

    response = {
        'data': res_data,
        'max': get_max_solar_day(from_, to_),
        "total_P_yesterday": get_yesterday(from_, to_),
        "total_P_today": get_today(from_, to_),
        "total_P_month": gat_month(from_, to_),
        "total_P_year": get_year(from_, to_),
    }

    return response


def get_today(page, page_size):
    from ..models import SolarHour
    from_ = (page * page_size) - (page_size - 1)
    to_ = page * page_size
    now = datetime.now()
    today_solar_sum = SolarHour.objects.filter(number_solar__range=(from_, to_), created_at__day=now.day,
                                               created_at__month=now.month,
                                               created_at__year=now.year).aggregate(total_sum=Sum('total_value'))
    return today_solar_sum['total_sum']


def gat_month(page, page_size):
    from ..models import SolarDay
    from_ = (page * page_size) - (page_size - 1)
    to_ = page * page_size
    now = datetime.now()
    month_solar_sum = SolarDay.objects.filter(number_solar__range=(from_, to_), created_at__month=now.month,
                                              created_at__year=now.year).aggregate(total_sum=Sum('total_value'))
    return month_solar_sum['total_sum']


def get_yesterday(page, page_size):
    from ..models import SolarDay
    from_ = (page * page_size) - (page_size - 1)
    to_ = page * page_size
    now = datetime.now().today() - timedelta(days=1)
    yesterday_solar_sum = SolarDay.objects.filter(number_solar__range=(from_, to_), created_at__day=now.day,
                                                  created_at__month=now.month, created_at__year=now.year).aggregate(
        total_sum=Sum('total_value'))
    return yesterday_solar_sum['total_sum']


def get_year(page, page_size):
    from ..models import SolarMonth
    from_ = (page * page_size) - (page_size - 1)
    to_ = page * page_size
    now = datetime.now().today()
    year_solar_sum = SolarMonth.objects.filter(created_at__year=now.year, number_solar__range=(from_, to_)).aggregate(
        total_sum=Sum('total_value'))
    return year_solar_sum['total_sum']


def get_max_solar_day(page, page_size):
    from ..models import Solar
    from_ = (page * page_size) - (page_size - 1)
    to_ = page * page_size
    solars = {}
    now = datetime.now().today()
    for i in range(from_, to_ + 1):
        solar = Solar.objects.filter(created_at__day=now.day, created_at__month=now.month, created_at__year=now.year,
                                     number_solar=i).order_by('-value').first()
        solars[f'solar_{solar.number_solar}']: solar
    return solars
