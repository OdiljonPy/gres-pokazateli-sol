from collections import defaultdict
from contextlib import suppress
from datetime import timedelta

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


def home(request):
    return render(request, 'home.html')


def total_p_sum(solar_objs):
    return round(sum(obj['total_P'] for obj in solar_objs), 2)


# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# def get_updates(request):
#     page = int(request.GET.get('page', 1))
#     page_size = int(request.GET.get('page_size', 2))
#     from_ = (page * page_size) - (page_size - 1)
#     to_ = page * page_size
#
#     now = timezone.now()
#     today = now - timedelta(hours=now.hour, minutes=now.minute, seconds=now.second)
#     yesterday = today - timedelta(days=1)
#     last_month = today - timedelta(days=(today.day - 1))
#     last_year = today - timedelta(days=timezone.now().timetuple().tm_yday - 1)
#
#     solar_objs_yesterday = Solar.objects.filter(
#         Q(time__gte=yesterday) & Q(time__lte=today) & Q(key='P_total') &
#         Q(number_solar__gte=from_) & Q(number_solar__lte=to_)
#     ).values('number_solar').annotate(total_P=Sum('value'))
#
#     solar_objs_today = Solar.objects.filter(
#         Q(time__gte=today) & Q(key='P_total') &
#         Q(number_solar__gte=from_) & Q(number_solar__lte=to_)
#     ).values('number_solar').annotate(total_P=Sum('value'))
#
#     solar_objs_month = Solar.objects.filter(
#         Q(time__gte=last_month) & Q(time__lte=now) & Q(key='P_total') &
#         Q(number_solar__gte=from_) & Q(number_solar__lte=to_)
#     ).values('number_solar').annotate(total_P=Sum('value'))
#
#     solar_objs_year = Solar.objects.filter(
#         Q(time__gte=last_year) & Q(time__lte=now) & Q(key='P_total') &
#         Q(number_solar__gte=from_) & Q(number_solar__lte=to_)
#     ).values('number_solar').annotate(total_P=Sum('value'))
#
#     result_data = defaultdict(dict)
#     for solar_object in create_solar_data_live():
#         key, value = list(solar_object.items())[0]
#         _, count = list(solar_object.items())[1]
#         result_data[key][value[0]] = value[1]
#         result_data[key]['count'] = count
#
#     result_data = dict(sorted(result_data.items(), key=lambda item: item[0]))
#     start_index = (int(page) - 1) * int(page_size)
#     end_index = start_index + int(page_size)
#     sliced_data = dict(list(result_data.items())[start_index:end_index])
#
#     start_solar = (page - 1) * page_size + 1
#     end_solar = start_solar + page_size
#     solar_objs = []
#     for i in range(start_solar, end_solar):
#         solar_obj = Solar.objects.filter(Q(time__gte=today) & Q(key='P_total') & Q(number_solar=i)).order_by(
#             '-value')[:1]
#         solar_objs.extend(solar_obj)
#         print(solar_objs[0].created_at)
#     serializer = ReadOnlySolarSerializer(solar_objs, many=True)
#     serializer_objects = serializer.data
#     solar_objects = defaultdict(list)
#     for solar_obj in serializer_objects:
#         solar_objects['solar_' + str(solar_obj['number_solar'])].append(solar_obj)
#     sliced_data_2 = dict(solar_objects)
#     return Response({"response": {
#         'data': sliced_data,
#         "max": sliced_data_2,
#         'total_P_yesterday': total_p_sum(solar_objs_yesterday),
#         'total_P_today': total_p_sum(solar_objs_today),
#         'total_P_month': total_p_sum(solar_objs_month),
#         'total_P_year': total_p_sum(solar_objs_year),
#     }, "ok": True}, status=status.HTTP_200_OK)


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


# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# def get_data(request):
#     page = int(request.GET.get('page', 1))
#     page_size = int(request.GET.get('page_size', 2))
#     from_ = (page * page_size) - (page_size - 1)
#     to_ = page * page_size
#     six_hours_before = timezone.now() - timedelta(hours=6)
#
#     data = {}
#     for number_solar in range(from_, to_ + 1):
#         array = []
#         start_time = six_hours_before
#         end_time = start_time + timedelta(minutes=30)
#         for _ in range(12):
#             solar_time_delta = Solar.objects.filter(
#                 Q(time__gte=start_time) & Q(time__lte=end_time)
#                 & Q(key='P_total') & Q(number_solar__gte=from_) & Q(number_solar__lte=to_)
#             ).values('number_solar').annotate(total_P=Sum('value'))
#             formatted_crated_at = end_time.strftime('%Y-%m-%d %H:%M:%S')
#             array.append({"value": total_p_sum(solar_time_delta), "created_at": formatted_crated_at})
#
#             start_time = end_time
#             end_time += timedelta(minutes=30)
#
#         data[f"solar_{number_solar}"] = array
#
#     return Response({"result": data, "ok": True}, status=status.HTTP_200_OK)
#

########################################################


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_updates(request):
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 2))

    return Response({"response": get_live(page, page_size), "ok": True}, status=status.HTTP_200_OK)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_data_api(request):
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 2))
    return Response(get_data(page, page_size), status=status.HTTP_200_OK)
