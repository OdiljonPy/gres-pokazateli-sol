from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests


def home(request):
    return render(request, 'home.html')


@api_view(['GET'])
def get_updates(request):
    # response = requests.get('http://10.10.20.1/crq?req=current')
    return Response(data={'ok': True}, status=status.HTTP_200_OK)
