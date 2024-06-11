from django.contrib import admin
from .models import Solar


# Register your models here.

@admin.register(Solar)
class SolarAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number_solar', 'key', 'value', 'crated_at_new')
