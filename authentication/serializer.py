from dj_rest_auth.serializers import TokenSerializer


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
        model = User
        fields = ('id', 'email','is_band')


class CustomTokenSerializer(TokenSerializer):
    user = UserTokenSerializer(read_only=True)

    class Meta(TokenSerializer.Meta):
        fields = ('key', 'user')