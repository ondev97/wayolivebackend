from django.urls import path,include
from . import views

urlpatterns = [
    path('register/',views.createuser.as_view()),
    path('updateuser/<int:pk>/',views.updateuser.as_view()),
    path('updateuserprofile/<int:pk>/',views.updateuserprofile),
    path('updatebandprofile/<int:pk>/',views.updatebandprofileview),
    path('listbands/',views.listbandprofiles),
    path('listusers/',views.listuserprofiles),
    path('viewprofile/',views.viewprofile),
    path('logout/',views.LogoutView.as_view()),
    path('notinevent/<int:id>/',views.getusersnotinevent),
]