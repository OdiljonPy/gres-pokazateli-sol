from django.urls import path

from .views import home, get_updates, get_solar_day, login, get_data

urlpatterns = [
    path('', home),
    path('get_data/', get_data),
    path('get_updates/', get_updates),
    path('solar_day/', get_solar_day),
    path('login/', login),

]
