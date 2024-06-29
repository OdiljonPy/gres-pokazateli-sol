from contextlib import suppress
from datetime import datetime
from django.utils import timezone

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings



def fetch_solar_data(url):
    from .exceptions import BadRequestException
    response = requests.Response()
    with suppress(Exception):
        response = requests.get(url)
    if response.status_code != 200:
        raise BadRequestException('Bad request or not containing solar data')
    return response.text.split('\r\n')[1:]


def parse_line(line, channels: dict) -> dict:
    data = line.split(',')
    if len(data) > 3:
        name, timestamp, value, status_value = data[:4]
        timestamp = timestamp.strip()
        datetime_str = timestamp.replace('w', '')
        created_at = datetime.strptime(datetime_str, "%d-%m-%Y %H:%M:%S.%f")
        if name in channels:
            number_solar, coefficient = channels.get(name)
            value = (float(value) / 1000) * coefficient
            return {
                'number_solar': number_solar,
                'name': name,
                'time': created_at,
                'value': round(value, 2),
                'status': int(status_value),
                'key': 'P_total'
            }
    return {}


def create_solar_data():
    from .serializers import SolarSerializer
    lines = fetch_solar_data('http://10.10.20.1/crq?req=current')
    P_total_channels = list(
        map(
            lambda i: [settings.SOLAR.get(i).get('P_total'), [i, settings.SOLAR.get(i).get('coefficient')]],
            list(range(1, len(settings.SOLAR) + 1)))
    )
    P_total_channels = dict(P_total_channels)

    for line in lines:
        solar_data = parse_line(line, P_total_channels)
        if solar_data:
            serializer = SolarSerializer(data=solar_data)
            if serializer.is_valid():
                serializer.save()
            continue
        continue


def create_background_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(create_solar_data, trigger='interval', seconds=5, timezone='UTC')
    scheduler.start()
    for i in scheduler.get_jobs():
        print(i)

