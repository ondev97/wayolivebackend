from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.exceptions import APIException
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from show.models import Enrollment
from .serializer import *

from .models import *

import random
from sms import send_sms
import openpyxl

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
@permission_classes([IsAuthenticated])
def viewprofile(request):
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

@api_view(['POST'])
def resetloginview(request):
    user = User.objects.filter(username=request.data['username']).first()
    if user and user.check_password(request.data['password']):
        user_token = Token.objects.filter(user=user)
        if user_token:
            user_token.delete()
            return Response({
                "msg":"Login session has been reset successfully"
            },status=200)
        else:
            return Response({
                "msg":"Login session with this username not found"
            },status=404)
    else:
        return Response({
            "msg":"Invalid credentials"
        },status=401)

def get_otp(phone):
    try:
        mobile = Phone.objects.get(mobile=phone)
    except ObjectDoesNotExist:
        Phone.objects.create(
            mobile=phone,
        )
        mobile = Phone.objects.get(mobile=phone)
    mobile.otp = str(random.randint(100000, 999999))
    mobile.save()

    return mobile

def verify_otp(phone, otp):
    response = {
        'is_verified': False
    }
    try:
        mobile = Phone.objects.get(mobile=phone)
    except ObjectDoesNotExist:
        response['message'] = "User does not exist"
        return response, 404

    if otp == mobile.otp:
        response['message'] = "You are authorised"
        response['is_verified'] = True
        return response, 200

    response['message'] = "OTP is wrong"
    return response, 400


class activate_user(APIView):
    @staticmethod
    def get(request, phone):
        mobile = get_otp(phone)

        try:
            send_sms(
                'Your verification code is ' + mobile.otp + '.\nWAYO LIVE!!!',
                '+12065550100',
                [mobile.mobile],
                fail_silently=False
            )
            return Response({"message": "OTP was sent successfully", "Mobile": mobile.mobile}, status=200)

        except:
            print("An exception occurred")
            return Response({"message": "Something is wrong", "Mobile": mobile.mobile}, status=503)

    @staticmethod
    def post(request, phone):
        response, status = verify_otp(phone, request.data["otp"])
        if response['is_verified']:
            user = User.objects.get(phone_no=phone)
            print(user)
            user.is_verified = True
            user.save()
            response['message'] = "You are verified"
        return Response(response, status=status)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def users_registration(request):
    excel_file = request.FILES["excel_file"]
    wb = openpyxl.load_workbook(excel_file)
    worksheet = wb["Sheet1"]
    worksheet.delete_rows(worksheet.min_row, 1)

    excel_data = list()
    for row in worksheet.iter_rows():
        row_data = list()
        for cell in row:
            row_data.append(str(cell.value))
        excel_data.append(row_data)

    users = User.objects.bulk_create(
        [
            User(username=row[0], password=make_password(row[1]), first_name=row[2], last_name=row[3], email=row[4], phone_no=row[5])
            for row in excel_data
        ], ignore_conflicts=True
    )

    return Response({
        "users": UserSerializer(users, many=True).data
    }, status=200)

