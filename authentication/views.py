from decouple import config
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from django.core.mail import send_mail

# Create your views here.
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.exceptions import APIException
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from show.models import Enrollment
from wayo.settings.base import EMAIL_HOST_USER
from .filter import UserProfileFilter
from .serializer import *
from django.db.models import Q

from .models import *

import random
from sms import send_sms
import openpyxl
import urllib
import requests

from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer


class createuser(CreateAPIView):
    serializer_class = UserSerializerAPI

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()


@api_view(['POST'])
def createuserview(request):
    phone_no = None
    email = None
    try:
        phone_no = request.data['phone_no']
        email = request.data['email']
    except Exception as e:
        print(e)

    if phone_no and phone_no[0] == '+':
        phone_no = phone_no[1:]

    if User.objects.filter(phone_no=phone_no).first():
        return Response({
            'phone_no': ['user with this phone number already exists.']
        }, status=400)
    #
    if len(phone_no) < 11 or len(phone_no) > 15 or phone_no[0] == '0':
        return Response({
            'phone_no': ['invalid phone number.']
        }, status=400)

    if User.objects.filter(email=email).first():
        return Response({
            'email': ['user with this email already exists.']
        }, status=400)

    user_seializer = UserSerializerAPI(data=request.data)
    if user_seializer.is_valid():
        user_seializer.save(phone_no=phone_no, password=make_password(request.data['password']))
        return Response(user_seializer.data, status=200)
    else:
        return Response(user_seializer.errors, status=400)


class updateuser(RetrieveUpdateAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializerAPI
    queryset = User.objects.all()

    def perform_update(self, serializer):
        user = User.objects.get(id=self.kwargs['pk'])
        if user.check_password(self.request.data['password']):
            instance = serializer.save()
            instance.set_password(instance.password)
            instance.save()
        else:
            raise APIException("Password's not matching")


@api_view(['PUT'])
def updateuserview(request, pk):
    user = User.objects.get(id=pk)
    password = None
    phone_no = None
    try:
        password = request.data['password']
        phone_no = request.data['phone_no']
    except Exception as e:
        print(e)

    if user and password and user.check_password(password):
        serializer = UserSerializerAPI(user, data=request.data)
        if serializer.is_valid():
            phone_no = (phone_no[1:] if phone_no[0] == '+' else phone_no) if phone_no else None
            if phone_no and phone_no[0] == '0':
                return Response({"message": "you should enter phone number with country code (ex: 93, 94)"}, status=400)
            if len(phone_no) > 10 and len(phone_no) <= 15:
                serializer.save(phone_no=phone_no, password=make_password(password))
                return Response(serializer.data)
            else:
                return Response({"phone": "Invalid phone number"}, status=400)

        else:
            return Response(serializer.errors, status=400)
    else:
        return Response({"message": "Invalid password"}, status=401)


@api_view(['POST'])
def updateuserviewwithOTP(request, pk):
    user = User.objects.get(id=pk)
    password = None
    phone_no = None
    is_local = None
    otp = None
    email = None
    try:
        password = request.data['password']
        phone_no = request.data['phone_no']
        email = request.data['email']
        otp = request.data['otp']
        phone_no = phone_no[1:] if phone_no[0] == '+' else phone_no
        is_local = phone_no.startswith('94')
    except Exception as e:
        print(e)

    # if not (phone_no and password and email and otp):
    #     return Response({
    #         "message": "Email, phone number, password and otp code are required"
    #     }, status=400)

    pre_otp = None
    if is_local:
        phone = Phone.objects.get(mobile=phone_no)
        if phone:
            pre_otp = phone.otp
    else:
        email = Email.objects.get(email=email)
        if email:
            pre_otp = email.otp

    if user and password and user.check_password(password):
        if(otp and pre_otp and otp == pre_otp):
            serializer = UserSerializerAPI(user, data=request.data)
            if serializer.is_valid():
                if phone_no and phone_no[0] == '0':
                    return Response({"phone": "you should enter phone number with country code (ex: 93, 94)"}, status=400)
                if len(phone_no) > 10 and len(phone_no) <= 15:
                    serializer.save(phone_no=phone_no, password=make_password(password))
                    return Response(serializer.data)
                else:
                    return Response({"phone": "Invalid phone number"}, status=400)

            else:
                return Response(serializer.errors, status=400)
        else:
            return Response({
                "message": "Invalid OTP"
            }, status=400)
    else:
        return Response({"password": "Invalid password"}, status=401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def updateuserprofile(request, pk):
    u = User.objects.get(id=pk)
    user = UserProfile.objects.get(user=u)
    serializer = UserProfileSerializer(instance=user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        serializer.data['user'].pop('password')
        return Response(serializer.data)
    else:
        return Response(serializer.errors)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def updatebandprofileview(request, pk):
    u = User.objects.get(id=pk)
    user = BandProfile.objects.get(user=u)
    serializer = BandProfileSerializer(instance=user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        serializer.data['user'].pop('password')
        return Response(serializer.data)
    else:
        return Response(serializer.errors)



@api_view(['GET'])
def listbandprofiles(request):
    bands = BandProfile.objects.all()
    serializer = ViewBandProfileSerializer(bands, many=True)
    for i in range(len(serializer.data)):
        serializer.data[i]['user'].pop('password')
    return Response(serializer.data)


@api_view(['GET'])
def listuserprofiles(request):
    users = UserProfile.objects.all()
    serializer = UserProfileSerializer(users, many=True)
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
@permission_classes([IsAuthenticated])
def getusersnotinevent(request, id):
    enr = Enrollment.objects.filter(event_id=id)
    enrollments = []
    for e in enr:
        enrollments.append(e.user.id)
    users = UserProfile.objects.exclude(id__in=enrollments)
    # users = UserProfile.objects.all()
    filtered_users = UserProfileFilter(request.GET, queryset=users)
    paginator = PageNumberPagination()
    paginator.page_size = 5
    result_page = paginator.paginate_queryset(filtered_users.qs, request)
    serializer = UserProfileSerializer(result_page, many=True)
    for i in range(len(serializer.data)):
        serializer.data[i]['user'].pop('password')
    return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
def TestLoginView(request):
    user = User.objects.filter(username=request.data['username']).first()
    response = {}
    if user and user.check_password(request.data['password']):
        response['user_id'] = user.id
        response['username'] = user.username
        response['is_verified'] = True if user.is_band else user.is_verified
        response['completed_user'] = False
        try:
            response['completed_user'] = True if user.first_name and user.last_name and user.email and user.phone_no else False
            response['phone_no'] = user.phone_no[1:] if user.phone_no[0] == '+' else user.phone_no
            response['email'] = user.email
        except Exception as e:
            pass
        token = Token.objects.filter(user=user).first()
        if token:
            response['status'] = False if user.is_band else True
        else:
            response['status'] = False
    else:
        return Response({'non_field_errors': ['Unable to log in with provided credentials.']}, status=400)
    return Response(response, status=200)


@api_view(['POST'])
def resetloginview(request):
    user = User.objects.filter(username=request.data['username']).first()
    if user and user.check_password(request.data['password']):
        user_token = Token.objects.filter(user=user)
        if user_token:
            user_token.delete()
            return Response({
                "msg": "Login session has been reset successfully"
            }, status=200)
        else:
            return Response({
                "msg": "Login session with this username not found"
            }, status=404)
    else:
        return Response({
            "msg": "Invalid credentials"
        }, status=401)


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


def get_otp_email(email):
    try:
        email = Email.objects.get(email=email)
    except ObjectDoesNotExist:
        Email.objects.create(
            email=email,
        )
        email = Email.objects.get(email=email)
    email.otp = str(random.randint(100000, 999999))
    email.save()

    return email


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


def verify_otp_email(email, otp):
    response = {
        'is_verified': False
    }
    try:
        email = Email.objects.get(email=email)
    except ObjectDoesNotExist:
        response['message'] = "User does not exist"
        return response, 404

    if otp == email.otp:
        response['message'] = "You are authorised"
        response['is_verified'] = True
        return response, 200

    response['message'] = "OTP is wrong"
    return response, 400


@api_view(['POST'])
def get_otp_code(request, username, email, phone_no):

    user = User.objects.filter(username=username).first()

    phone_no = phone_no[1:] if phone_no[0] == '+' else phone_no

    if len(phone_no) < 11 or len(phone_no) > 15 or phone_no[0] == '0':
        return Response({
            "phone": "Invalid phone number"
        }, status=400)

    email_user = User.objects.filter(email=email).first()
    phone_no_user = User.objects.filter(phone_no=phone_no).first()

    if email_user and user != email_user:
        return Response({
            "email": "This email is already taken."
        }, status=400)

    if phone_no_user and user != phone_no_user:
        return Response({
            "phone": "This phone number is already taken."
        }, status=400)

    if user:
        if not user.check_password(request.data['password']):
            return Response({
                'password': 'wrong password'
            }, status=400)

        if phone_no.startswith('94'):
            mobile = get_otp(phone_no)
            verify_msg = 'Your OTP is ' + mobile.otp + ' to update your account on WAYO.LIVE.'
            params = {
                'id': config('TEXTIT_ID'),
                'pw': config('TEXTIT_PW'),
                'to': mobile.mobile,
                'text': verify_msg,
            }
            url = 'https://www.textit.biz/sendmsg/?' + urllib.parse.urlencode(params)
            try:
                response = requests.get(url)
                # text = "OK:Cr=0.71,Route=CSID-WAYO,MessageID=7171-1627019618,Recipient=754745340,BX=23-152\n"
                if response.text.split(':')[0] == 'OK':
                    return Response({
                        "message": "Verification code sent successfully",
                        "mobile": mobile.mobile,
                        "res": response.text
                    }, status=200)
                else:
                    return Response({
                        "message": "Verification code was not sent",
                        "mobile": mobile.mobile,
                        "res": response.text
                    }, status=400)
            except Exception as e:
                print("An exception occurred", e)
                return Response({"message": "Something is wrong", "mobile": mobile.mobile}, status=503)
        else:
            email_obj = get_otp_email(email)
            verify_msg = 'Your OTP is ' + email_obj.otp + ' to update your account on WAYO.LIVE.'
            subject = 'Update WAYO.LIVE account'
            try:
                send_mail(subject, verify_msg, EMAIL_HOST_USER, [email_obj.email], fail_silently=False)
                response = {
                    "message": "Verification code sent successfully",
                    "mobile": email_obj.email
                }
                return Response(response, status=200)

            except Exception as e:
                print('Error : ', e)
                response = {
                    "message": "Verification code was not sent",
                    "email": email_obj.email,
                    'test': email
                }
                return Response(response, status=400)
    else:
        return Response({
            "message": "User does not exist or has not set a phone number and an email"
        }, status=400)


class reset_session(APIView):
    @staticmethod
    def get(request, username):
        user = User.objects.filter(username=username).first()
        if user.phone_no and user.email:
            if user.phone_no.startswith('94') or user.phone_no.startswith('+94'):
                mobile = get_otp(user.phone_no[1:] if user.phone_no[0] == '+' else user.phone_no)
                verify_msg = 'Your OTP is ' + mobile.otp + ' to reset login session of your WAYO.LIVE account.'
                params = {
                    'id': config('TEXTIT_ID'),
                    'pw': config('TEXTIT_PW'),
                    'to': mobile.mobile,
                    'text': verify_msg,
                }
                url = 'https://www.textit.biz/sendmsg/?' + urllib.parse.urlencode(params)
                try:
                    response = requests.get(url)
                    # text = "OK:Cr=0.71,Route=CSID-WAYO,MessageID=7171-1627019618,Recipient=754745340,BX=23-152\n"
                    if response.text.split(':')[0] == 'OK':
                        return Response({
                            "message": "Verification code sent successfully",
                            "mobile": mobile.mobile[1:] if mobile.mobile[0] == '+' else mobile.mobile,
                            "res": response.text
                        }, status=200)
                    else:
                        return Response({
                            "message": "Verification code was not sent",
                            "mobile": mobile.mobile[1:] if mobile.mobile[0] == '+' else mobile.mobile,
                            "res": response.text
                        }, status=400)
                except:
                    print("An exception occurred")
                    return Response({"message": "Something is wrong", "mobile": mobile.mobile}, status=503)
            else:
                email_obj = get_otp_email(user.email)
                verify_msg = 'Your OTP is ' + email_obj.otp + ' to reset login session of your WAYO.LIVE account.'
                subject = 'Verify WAYO.LIVE account'
                try:
                    send_mail(subject, verify_msg, EMAIL_HOST_USER, [user.email], fail_silently=False)
                    response = {
                        "message": "Verification code sent successfully",
                        "mobile": email_obj.email
                    }
                    return Response(response, status=200)

                except Exception as e:
                    print('Error : ', e)
                    response = {
                        "message": "Verification code was not sent",
                        "email": email_obj.email
                    }
                    return Response(response, status=400)
        else:
            return Response({
                "msg": "User has not set a phone number and an email"
            }, status=400)

    @staticmethod
    def post(request, username):
        user = User.objects.filter(username=username).first()
        if user:
            if user.phone_no and user.email:
                if user.phone_no.startswith('94'):
                    mobile = Phone.objects.get(mobile=user.phone_no)
                    if mobile.otp == request.data['otp']:
                        user_token = Token.objects.filter(user=user)
                        if user_token:
                            user_token.delete()
                            token = Token.objects.create(user=user)
                            serializer = OTPCustomTokenSerializer(token)
                            return Response({
                                "msg": "Login session has been reset successfully",
                                "token": serializer.data
                            }, status=200)
                        else:
                            return Response({
                                "msg": "Login session with this username not found"
                            }, status=404)
                    else:
                        return Response({
                            "msg": "OTP is wrong"
                        }, status=400)
                else:
                    email_obj = Email.objects.get(email=user.email)
                    if email_obj.otp == request.data['otp']:
                        user_token = Token.objects.filter(user=user)
                        if user_token:
                            user_token.delete()
                            token = Token.objects.create(user=user)
                            serializer = OTPCustomTokenSerializer(token)
                            return Response({
                                "msg": "Login session has been reset successfully",
                                "token": serializer.data
                            }, status=200)
                        else:
                            return Response({
                                "msg": "Login session with this username not found"
                            }, status=404)
                    else:
                        return Response({
                            "msg": "OTP is wrong"
                        }, status=400)
            else:
                return Response({
                    "msg": "User has not set a phone number and an email"
                }, status=400)
        else:
            return Response({
                "msg": "Invalid username"
            }, status=401)


class activate_user(APIView):
    @staticmethod
    def get(request, phone):
        mobile = get_otp(phone[1:] if phone[0] == '+' else phone)
        verify_msg = 'Your OTP is ' + mobile.otp + ' to verify WAYO.LIVE account.'
        params = {
            'id': config('TEXTIT_ID'),
            'pw': config('TEXTIT_PW'),
            'to': mobile.mobile,
            'text': verify_msg,
        }
        url = 'https://www.textit.biz/sendmsg/?' + urllib.parse.urlencode(params)
        try:
            response = requests.get(url)
            # text = "OK:Cr=0.71,Route=CSID-WAYO,MessageID=7171-1627019618,Recipient=754745340,BX=23-152\n"
            if response.text.split(':')[0] == 'OK':
                return Response({
                    "message": "Verification code sent successfully",
                    "mobile": mobile.mobile[1:] if mobile.mobile[0] == '+' else mobile.mobile,
                    "res": response.text
                }, status=200)
            else:
                return Response({
                    "message": "Verification code was not sent",
                    "mobile": mobile.mobile[1:] if mobile.mobile[0] == '+' else mobile.mobile,
                    "res": response.text
                }, status=400)
        except:
            print("An exception occurred")
            return Response({"message": "Something is wrong", "mobile": mobile.mobile}, status=503)

    @staticmethod
    def post(request, phone):
        response, status = verify_otp(phone[1:] if phone[0] == '+' else phone, request.data["otp"])
        if response['is_verified']:
            user = User.objects.get(Q(phone_no=phone[1:] if phone[0] == '+' else '+' + phone) | Q(phone_no=phone))
            token = Token.objects.create(user=user)
            user.is_verified = True
            user.save()
            serializer = OTPCustomTokenSerializer(token)
            response['message'] = "You are verified"
            response['token'] = serializer.data
        return Response(response, status=status)

@permission_classes([IsAuthenticated])
class activate_user_by_email(APIView):
    @staticmethod
    def get(request, email):
        email_obj = get_otp_email(email)
        verify_msg = 'Your OTP is ' + email_obj.otp + ' to verify WAYO.LIVE account.'
        subject = 'Verify WAYO.LIVE account'
        try:
            send_mail(subject, verify_msg, EMAIL_HOST_USER, [email], fail_silently=False)
            response = {
                "message": "Verification code sent successfully",
                "mobile": email_obj.email
            }
            return Response(response, status=200)

        except Exception as e:
            print('Error : ', e)
            response = {
                "message": "Verification code was not sent",
                "email": email_obj.email
            }
            return Response(response, status=400)

    @staticmethod
    def post(request, email):
        response, status = verify_otp_email(email, request.data["otp"])
        if response['is_verified']:
            user = User.objects.get(email=email)
            token = Token.objects.create(user=user)
            print('Token', token)
            user.is_verified = True
            user.save()
            serializer = OTPCustomTokenSerializer(token)
            response['message'] = "You are verified"
            response['token'] = serializer.data
        return Response(response, status=status)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def users_registration(request):
    usernames = request.data['USERNAME']
    passwords = request.data['PASSWORD']

    users = [
        User(username=usernames[row], password=make_password(passwords[row]))
        for row in range(len(usernames))
    ]
    not_saved = list()
    i = 1
    try:
        User.objects.bulk_create(users)
    except:
        for user in users:
            try:
                user.save()
            except:
                not_saved.append(i)
            i+=1

    return Response({
        "count_of_all_users": len(usernames),
        "not_saved_lines": not_saved
    }, status=200)


class MyExampleViewSet(XLSXFileMixin, ReadOnlyModelViewSet):
    queryset = User.objects.filter(userprofile=None, is_superuser=False, is_band=False)
    serializer_class = UserSerializer
    renderer_classes = (XLSXRenderer,)
    filename = 'my_export.xlsx'
    column_header = {
        'column_width': [30, 30, 30, 30, 30],
        'height': 25,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        }
    }
    body = {
        'style': {
            'alignment': {
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 10,
                'bold': False,
                'color': 'FF000000',
            }
        },
        'height': 20,
    }

