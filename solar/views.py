from collections import defaultdict
from contextlib import suppress
from datetime import timedelta

# from .task_daily import task_daily
# from .task_hourly import task_hourly
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Solar
from .serializers import ReadOnlySolarSerializer, SolarGetUpdatesSerializer
# from .utils import create_solar_data_live
from .repo.get_updates import get_live
from .repo.get_data import get_data
from django.conf import settings

# from .task_monthly import task_solar_month
# from .task_yearly import task_solar_yearly
from .utils import create_background_task


def home(request):
    from .models import Solar
    import datetime
    # Create your tests here.

    lst = [80, 90, 100, 110, 150, 200, 230, 400]

    for num in range(1, 5):
        for i in lst:
            solar = Solar.objects.create(number_solar=num, name='G275', time=datetime.datetime.now(), value=i, status=0,
                                         key='P_total')
            solar.save()
    return render(request, 'home.html')


def total_p_sum(solar_objs):
    return round(sum(obj['total_P'] for obj in solar_objs), 2)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_solar_day(request):
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 2))
    now = timezone.now()
    solar_objs = []
    today = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
    start_solar = (page - 1) * page_size + 1
    end_solar = start_solar + page_size
    for i in range(start_solar, end_solar):
        solar_obj = Solar.objects.filter(Q(created_at__gte=today) & Q(key='P_total') & Q(number_solar=i)).order_by(
            '-created_at')[:24]
        res = list(map(lambda x: solar_obj[x], range(1, 25, 2)))
        solar_objs.extend(res)
    solar_objects = defaultdict(list)
    serializer = ReadOnlySolarSerializer(solar_objs, many=True)
    serializer_objects = serializer.data

    for solar_obj in serializer_objects:
        solar_objects['solar_' + str(solar_obj['number_solar'])].append(solar_obj)
    sliced_data = dict(solar_objects)

    return Response(data={'response': sliced_data, "ok": True}, status=status.HTTP_200_OK)


@api_view(['POST'])
def login(request):
    data = request.data
    username = data.get('username', None)
    password = data.get('password', None)
    user = User.objects.filter(username=username).first()
    if username and password and user:
        if user.check_password(password):
            refresh_token = RefreshToken.for_user(user)
            access_token = str(refresh_token.access_token)
            return Response({'result': {'access_token': access_token, 'refresh_token': str(refresh_token)}, 'ok': True},
                            status=status.HTTP_200_OK)
        return Response({'result': "", 'error': "The password was entered incorrectly ", 'ok': False},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response({'result': "", 'error': "The username or password was not entered", 'ok': False},
                    status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_updates(request):
    print("hello")
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 2))
    print("hello2")
    return Response({"response": get_live(page, page_size), "ok": True}, status=status.HTTP_200_OK)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_data_api(request):
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 2))
    return Response(get_data(page, page_size), status=status.HTTP_200_OK)


@api_view(['GET'])
def run_scheduler_api(request):
    from .create import create_task
    if settings.SCHEDULER == 0:
        create_task()
        create_background_task()
        settings.SCHEDULER = 1
        return Response({"ok": True}, status=status.HTTP_200_OK)

    return Response({"ok": False, "message": "already running"}, status=status.HTTP_400_BAD_REQUEST)
