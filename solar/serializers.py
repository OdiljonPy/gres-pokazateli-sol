from django.conf import settings
from rest_framework import serializers

from .models import Solar


class SolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solar
        fields = ['id', 'number_solar', 'name', 'time', 'status', 'value', 'created_at', 'key', 'time']

    def create(self, validated_data):
        coefficient = settings.SOLAR.get(validated_data['number_solar']).get('coefficient')
        validated_data['value'] = round((validated_data['value'] / 1000) * coefficient, 2)
        return super(SolarSerializer, self).create(validated_data)


class ReadOnlySolarSerializer(SolarSerializer):
    class Meta(SolarSerializer.Meta):
        fields = ['id', 'number_solar', 'value', 'key', 'created_at', "time"]

    def to_representation(self, instance):
        formatted_crated_at = instance.created_at.strftime('%Y-%m-%d %H:%M')
        data = {
            'id': instance.id,
            'number_solar': instance.number_solar,
            instance.key: instance.value,
            'crated_at': formatted_crated_at,
        }

        return data


class SolarGetUpdatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solar
        fields = ['number_solar', 'value', 'key']

    def to_representation(self, instance):
        data = {
            f"solar_{instance.number_solar}": (f"{instance.key}", instance.value),
            'count': settings.SOLAR.get(instance.number_solar).get('count')
        }
        return data
