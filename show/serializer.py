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


