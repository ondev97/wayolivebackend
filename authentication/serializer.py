from dj_rest_auth.app_settings import TokenSerializer
from django.contrib.auth import get_user_model

from authentication.models import User,BandProfile,UserProfile
from rest_framework import serializers


class UserSerializerAPI(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email','password','phone_no']
        extra_kwargs = {"password":{"write_only":True}}


class BandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandProfile
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'email','is_band')


class CustomTokenSerializer(TokenSerializer):
    user = UserTokenSerializer(read_only=True)

    class Meta(TokenSerializer.Meta):
        fields = ('key', 'user')