import random

from rest_framework import serializers
from .models import Solar
from django.conf import settings

# class SolarSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Solar
#         fields = ['id', 'number_solar', 'name', 'time', 'status', 'value', 'crated_at', 'key']
#
#     def create(self, validated_data):
#         coefficient = settings.SOLAR.get(validated_data['number_solar']).get('coefficient')
#         validated_data['value'] = round((validated_data['value'] / 1000) * coefficient, 2)
#         return super(SolarSerializer, self).create(validated_data)
#
#
# class ReadOnlySolarSerializer(SolarSerializer):
#     class Meta(SolarSerializer.Meta):
#         fields = ['id', 'number_solar', 'value', 'key', 'crated_at']
#
#     def to_representation(self, instance):
#         data = {
#             'id': instance.id,
#             'number_solar': instance.number_solar,
#             instance.key: instance.value,
#             'crated_at': instance.crated_at
#         }
#
#         return data


from rest_framework import serializers
from .models import Solar
from django.conf import settings


class SolarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solar
        fields = ['id', 'number_solar', 'name', 'time', 'status', 'value', 'crated_at', 'key']

    def create(self, validated_data):
        coefficient = settings.SOLAR.get(validated_data['number_solar']).get('coefficient')
        validated_data['value'] = round((validated_data['value'] / 1000) * coefficient, 2)
        return super(SolarSerializer, self).create(validated_data)


class ReadOnlySolarSerializer(SolarSerializer):
    class Meta(SolarSerializer.Meta):
        fields = ['id', 'number_solar', 'value', 'key', 'crated_at']

    def to_representation(self, instance):
        data = {
            'id': instance.id,
            'number_solar': instance.number_solar,
            instance.key: instance.value,
            'crated_at': instance.crated_at
        }

        return data


class SolarGetUpdatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solar
        fields = ['number_solar', 'value', 'key']

    def to_representation(self, instance):
        data = {
            f"solar_{instance.number_solar}": (f"{instance.key}", instance.value)
        }
        return data
