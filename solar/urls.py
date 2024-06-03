from django.urls import path
from .views import home, get_updates

urlpatterns = [
    path('', home),
    path('get_updates/', get_updates)
]
