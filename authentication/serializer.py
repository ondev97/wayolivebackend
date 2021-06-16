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