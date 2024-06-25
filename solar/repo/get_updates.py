from contextlib import suppress
from datetime import datetime

import requests
from django.conf import settings

from ..exceptions import BadRequestException

SOLAR = settings.SOLAR


def get_datetime() -> dict:
    now = datetime.today()
    return {
        'yesterday': now.day - 1 if now.day - 1 > 9 else f"0{now.day - 1}",
        'today': now.day if now.day > 9 else f"0{now.day}",
        'tomorrow': now.day + 1 if now.day + 1 > 9 else f"0{now.day + 1}",
        'month': now.month if now.month > 9 else f"0{now.month}",
        'next_month': now.month + 1 if now.month + 1 > 9 else f"0{now.month + 1}",
        'year': now.year,
    }


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


def total_P_yesterday(channels, date: dict) -> float:
    real_rows = safe_request(
        url=f"http://195.69.218.121/crq?req=archive&type=g&interval=day&"
            f"t1={date.get('year')}{date.get('month')}{date.get('yesterday')}000000")
    return round(get_solar_data(channels, real_rows), 2)


def total_P_today(channels, date: dict) -> float:
    real_rows = safe_request(
        url=f"http://195.69.218.121/crq?req=archive&type=g&interval=main&"
            f"t1={date.get('year')}{date.get('month')}{date.get('today')}000000&"
            f"t2={date.get('year')}{date.get('month')}{date.get('tomorrow')}000000")
    return round(get_solar_data(channels, real_rows), 2)


def total_P_month(channels, date: dict) -> float:
    real_rows = safe_request(
        url=f"http://195.69.218.121/crq?req=archive&type=g&interval=day&"
            f"t1={date.get('year')}{date.get('month')}010000000&t2={date.get('year')}{date.get('next_month')}01000000")
    return round(get_solar_data(channels, real_rows), 2)


def total_P_year(channels, date: dict) -> float:
    real_rows = safe_request(
        url=f"http://195.69.218.121/crq?req=archive&type=g&interval=month&"
            f"t1={date.get('year')}0101000000&t2={date.get('year')}1231000000")
    return round(get_solar_data(channels, real_rows), 2)


def get_channel_data_for_lifetime() -> dict:
    real_rows = safe_request(
        url="http://195.69.218.121/crq?req=current"
    )
    res = {}
    for row in real_rows.split('\n')[2:]:
        if len(row.split(',')) > 3:
            res[row.split(',')[0]] = float(row.split(',')[2])
    return res


def get_max_solar(from_, to_, date: dict) -> dict:
    real_rows = safe_request(
        url=f"http://195.69.218.121/crq?req=archive&type=g&interval=main&"
            f"t1={date.get('year')}{date.get('month')}{date.get('today')}000000&"
            f"t2={date.get('year')}{date.get('month')}{date.get('tomorrow')}000000")
    all_list = list(map(lambda solar_n: list(
        filter(lambda x: x.split(',')[0] == SOLAR.get(solar_n).get('P_total') and len(x.split(',')) > 3,
               real_rows.split('\n')[2:])) + [solar_n], list(range(from_, to_ + 1))))

    response = dict()
    for list_item in all_list:
        if len(list_item) > 1:
            number_solar = list_item.pop(-1)
            max_solar = sorted(list_item, key=lambda x: float(x.split(',')[2].strip()), reverse=True)[0]
            time = max_solar.split(',')[1].strip().replace('w', '')
            formatted_created_at = datetime.strptime(time, '%d-%m-%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            response[f"solar_{number_solar}"] = [
                {
                    "id": 1,
                    "number_solar": number_solar,
                    "P_total": (float(max_solar.split(',')[2].strip()) / 1000) * SOLAR.get(number_solar).get(
                        'coefficient'),
                    "created_at": formatted_created_at
                }
            ]
    return response


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
                    'I_1': round(all_channels.get(SOLAR.get(i).get('I_1'), 0.0), 2),
                    'I_2': round(all_channels.get(SOLAR.get(i).get('I_2'), 0.0), 2),
                    'I_3': round(all_channels.get(SOLAR.get(i).get('I_3'), 0.0), 2),
                    'count': SOLAR.get(i).get('count')
                }
        }, list(range(from_, to_ + 1)))
    )
    date = get_datetime()

    P_total_channels = list(
        map(lambda i: [SOLAR.get(i).get('P_total'), SOLAR.get(i).get('coefficient')], list(range(from_, to_ + 1)))
    )
    P_total_channels = dict(P_total_channels)

    res_data = {}
    for item in data:
        res_data[list(item.keys())[0]] = list(item.values())[0]

    response = {
        'data': res_data,
        'max': get_max_solar(from_, to_, date),
        "total_P_yesterday": total_P_yesterday(P_total_channels, date),
        "total_P_today": total_P_today(P_total_channels, date),
        "total_P_month": total_P_month(P_total_channels, date),
        "total_P_year": total_P_year(P_total_channels, date),
    }

    return response
