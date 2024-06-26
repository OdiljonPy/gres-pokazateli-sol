from django.conf import settings
from rest_framework import serializers

from .models import Solar, SolarDay


class SolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solar
        fields = ['id', 'number_solar', 'name', 'time', 'status', 'value', 'created_at', 'key', 'time']


class ReadOnlySolarSerializer(SolarSerializer):
    class Meta(SolarSerializer.Meta):
        fields = ['id', 'number_solar', 'value', 'key', 'created_at', "time"]

    def to_representation(self, instance):
        formatted_crated_at = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'id': instance.id,
            'number_solar': instance.number_solar,
            instance.key: instance.value,
            'created_at': formatted_crated_at,
        }

        return data


class ReadOnlySolarDAYSerializer(serializers.ModelSerializer):
    class Meta(SolarSerializer.Meta):
        model = SolarDay
        fields = ['id', 'number_solar', 'total_value', 'created_at']

    def to_representation(self, instance):
        formatted_crated_at = instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'id': instance.id,
            'number_solar': instance.number_solar,
            instance.key: instance.value,
            'created_at': formatted_crated_at,
        }

        return data


class SolarGetUpdatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solar
        fields = ['number_solar', 'value', 'key']

    def to_representation(self, instance):
        data = {
            f"solar_{instance.get('number_solar')}": (f"{instance.get('key')}", instance.get('value')),
            'count': settings.SOLAR.get(instance.get('number_solar')).get('count')
        }
        return data
