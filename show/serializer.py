from rest_framework import serializers
from .models import *


class EventModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMode
        fields = '__all__'


class EventModeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMode
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

        depth = 2


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"


class EnrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = "__all__"


class MyEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['event', 'ticket_number']
        depth = 2


class AudienceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model=AudienceDataForm
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

