from dj_rest_auth.app_settings import TokenSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import *


class ConcertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concert
        fields = '__all__'

class ConcertListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concert
        fields = '__all__'

        depth = 2


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class EventViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

        depth = 1


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class EnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = "__all__"


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email','is_band')


class CustomTokenSerializer(TokenSerializer):
    user = UserTokenSerializer(read_only=True)

    class Meta(TokenSerializer.Meta):
        fields = ('key', 'user')