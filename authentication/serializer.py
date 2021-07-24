from dj_rest_auth.serializers import TokenSerializer

from authentication.models import User, BandProfile, UserProfile
from rest_framework import serializers


class UserSerializerAPI(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_no', 'first_name', 'last_name']
        extra_kwargs = {"password": {"write_only": True}}


class BandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandProfile
        fields = '__all__'
        depth = 1


class ViewBandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandProfile
        fields = '__all__'
        depth = 1


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        depth = 1


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_band', 'is_verified','phone_no')


class CustomTokenSerializer(TokenSerializer):
    user = UserTokenSerializer(read_only=True)

    class Meta(TokenSerializer.Meta):
        fields = ('key', 'user')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_no', 'first_name', 'last_name']
