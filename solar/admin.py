from django.contrib import admin
from .models import Solar, SolarHour, SolarDay, SolarMonth, SolarYear


# Register your models here.

@admin.register(Solar)
class SolarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number_solar', 'key', 'value', 'created_at')


@admin.register(SolarHour)
class SolarHourAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number_solar', 'total_value', 'created_at')


@admin.register(SolarDay)
class SolarHourAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number_solar', 'total_value', 'created_at')


@admin.register(SolarMonth)
class SolarHourAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number_solar', 'total_value', 'created_at')


@admin.register(SolarYear)
class SolarHourAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number_solar', 'total_value', 'created_at')
