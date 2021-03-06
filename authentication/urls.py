from django.urls import path,include
from . import views

urlpatterns = [
    path('register/',views.createuserview),
    path('updateuser/<int:pk>/',views.updateuserview),
    path('updateuserotp/<int:pk>/',views.updateuserviewwithOTP),
    path('updateuserprofile/<int:pk>/',views.updateuserprofile),
    path('updatebandprofile/<int:pk>/',views.updatebandprofileview),
    path('listbands/',views.listbandprofiles),
    path('listusers/',views.listuserprofiles),
    path('viewprofile/',views.viewprofile),
    path('logout/',views.LogoutView.as_view()),
    path('checkuser/',views.TestLoginView),
    path('notinevent/<int:id>/',views.getusersnotinevent),
    path('deletetoken/',views.resetloginview),
    path('activate_user/<str:phone>/', views.activate_user.as_view()),
    path('activate_user_by_email/<str:email>/', views.activate_user_by_email.as_view()),
    path('resetsession/<str:username>/', views.reset_session.as_view()),
    path('getotp/<str:username>/<str:email>/<str:phone_no>/', views.get_otp_code),
    path('reg_users/',views.users_registration),
    path('unverified/',views.MyExampleViewSet.as_view({'get': 'list'})),
]