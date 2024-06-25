from django.urls import path

from .views import home, get_updates, get_solar_day, login, get_data_api, get_live

urlpatterns = [
    path('', home),
    path('get_data/', get_data_api),
    path('get_updates/', get_updates),
    path('get_live/', get_live),
    path('solar_day/', get_solar_day),
    path('login/', login),

]
