from django.urls import path

from .views import home, get_updates, get_solar_day, login, get_data_api, get_live, run_scheduler_api, get_year

urlpatterns = [
    path('', home),
    path('get_data/', get_data_api),
    path('get_updates/', get_updates),
    path('get_live/', get_live),
    path('solar_day/', get_solar_day),
    path('get_year/', get_year),
    path('login/', login),


    path('scheduler/run/', run_scheduler_api)

]
