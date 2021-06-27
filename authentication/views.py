from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.exceptions import APIException
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from show.models import Enrollment
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
@parser_classes([MultiPartParser,FormParser])
def updateuserprofile(request, pk):
    user = UserProfile.objects.get(user_id=pk)
    serializer = UserProfileSerializer(instance=user,data=request.data)
    if serializer.is_valid():
        serializer.save()
        serializer.data['user'].pop('password')
        return Response(serializer.data)
    else:
        return Response(serializer.errors)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser,FormParser])
def updatebandprofileview(request,pk):
    user = BandProfile.objects.get(user_id=pk)
    serializer = BandProfileSerializer(instance=user,data=request.data)
    if serializer.is_valid():
        serializer.save()
        serializer.data['user'].pop('password')
    return Response(serializer.data)


@api_view(['GET'])
def listbandprofiles(request):
    bands = BandProfile.objects.all()
    serializer = ViewBandProfileSerializer(bands,many=True)
    for i in range(len(serializer.data)):
        serializer.data[i]['user'].pop('password')
    return Response(serializer.data)

@api_view(['GET'])
def listuserprofiles(request):
    users = UserProfile.objects.all()
    serializer = UserProfileSerializer(users,many=True)
    for i in range(len(serializer.data)):
        serializer.data[i]['user'].pop('password')
    return Response(serializer.data)

@api_view(['GET'])
def viewprofile(request):
    print(request.user.username, request.user.is_band)
    if request.user.is_band:
        user = BandProfile.objects.get(user=request.user)
        serializer = BandProfileSerializer(user)
    else:
        user = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user)
    serializer.data['user'].pop('password')
    return Response(serializer.data)

# Logout View
class LogoutView(APIView):
    @staticmethod
    def delete(request, *args, **kwargs):
        request.user.auth_token.delete()
        data = {
            "message": "You have successfully logged out.",
        }
        return Response(data)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def getusersnotinevent(request, id):
    enr = Enrollment.objects.filter(event_id=id)
    enrollments = []
    for e in enr:
        enrollments.append(e.user.id)
    users = UserProfile.objects.exclude(id__in=enrollments)
    serializer = UserProfileSerializer(users,many=True)
    for i in range(len(serializer.data)):
        serializer.data[i]['user'].pop('password')
    return Response(serializer.data)


@api_view(['POST'])
def TestLoginView(request):
    user = User.objects.filter(username=request.data['username']).first()
    status = False
    if not user:
        return Response({
            "status": status
        })
    token = Token.objects.filter(user=user).first()
    if token:
        status = True
    return Response({
        "status" : status
    })

@api_view(['GET'])
def resetloginview(request,username):
    user_token = Token.objects.get(username=username)
    if user_token:
        user_token.delete()
        return Response({
            "msg":"Login Session Reset Successfully"
        })
    else:
        return Response({
            "msg":"Login Session with this Username not Found"
        })
