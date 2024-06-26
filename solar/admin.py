from django.contrib import admin
from .models import Solar, SolarHour


# Register your models here.

@admin.register(Solar)
class SolarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number_solar', 'key', 'value')



@admin.register(SolarHour)
class SolarHourAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number_solar',  'total_value')
