from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializer import *

from .models import *

class createuser(CreateAPIView):
    serializer_class = UserSerializerAPI

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()



class updateuser(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializerAPI
    queryset = User.objects.all()

    def perform_update(self, serializer):
        if self.request.user.check_password(self.request.data['password']):
            instance = serializer.save()
            print(instance.password)
            instance.set_password(instance.password)
            instance.save()
        else:
            print("not matched")
            raise APIException("Password's not matching")



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updatestudentprofileView(request,pk):
    user = UserProfile.objects.get(user_id=pk)
    serializer = UserProfileSerializer(instance=user,data=request.data)
    if serializer.is_valid():
        serializer.save()
        serializer.data['user'].pop('password')
    return Response(serializer.data)



