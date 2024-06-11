import random
import requests
from django.conf import settings
from .exceptions import BadRequestException
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


def fetch_solar_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise BadRequestException('Bad request or not containing solar data')
    return response.text.split('\r\n')


def parse_line(line, solar_lookup):
    data = line.split(',')
    if len(data) > 3:
        name, timestamp, value, status_value = data[:4]
        timestamp = timestamp.strip()
        datetime_str = timestamp.replace('w', '')
        created_at = datetime.strptime(datetime_str, "%d-%m-%Y %H:%M:%S.%f")
        if name in solar_lookup:
            number_solar, key = solar_lookup[name]
            return {
                'number_solar': number_solar,
                'name': name,
                'time': created_at,
                'value': float(value),
                'status': int(status_value),
                'key': key
            }
    return None


def create_solar_data():
    from .serializers import SolarSerializer
    lines = fetch_solar_data('http://10.10.20.1/crq?req=current')
    solar_lookup = {v: (idx + 1, k) for idx, solar in enumerate(settings.SOLAR.values()) for k, v in solar.items()}
    solar_objects = []

    for line in lines:
        solar_data = parse_line(line, solar_lookup)
        if solar_data:
            serializer = SolarSerializer(data=solar_data)
            if serializer.is_valid():
                solar_obj = serializer.save()
                solar_objects.append(solar_obj)
    return solar_objects


def create_solar_data_live():
    from .serializers import SolarSerializer
    from .models import Solar
    lines = fetch_solar_data('http://10.10.20.1/crq?req=current')
    solar_lookup = {v: (idx + 1, k) for idx, solar in enumerate(settings.SOLAR.values()) for k, v in solar.items()}
    solar_objects = []

    for line in lines:
        solar_data = parse_line(line, solar_lookup)
        if solar_data:
            serializer = SolarSerializer(data=solar_data)
            if serializer.is_valid():
                number_solar = serializer.data.get('number_solar')
                value = serializer.data.get('value')
                coefficient = settings.SOLAR.get(number_solar).get('coefficient')
                value = round((value / 1000) * coefficient, 2)
                new_solar = Solar(
                    number_solar=number_solar,
                    name=serializer.data.get('name'),
                    time=serializer.data.get('time'),
                    value=value,
                    status=serializer.data.get('status'),
                    key=serializer.data.get('key')
                )
                solar_objects.append(new_solar)
    return solar_objects


def create_background_task():
    scheduler = BackgroundScheduler()
    scheduler.add_job(create_solar_data, trigger='interval', seconds=2, timezone='Asia/Tashkent')
    scheduler.start()
