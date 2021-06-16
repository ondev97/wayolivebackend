from django.urls import path,include
from . import views

urlpatterns = [
    path('register/',views.createuser.as_view()),
    path('updateuser/<int:pk>/',views.updateuser.as_view()),
    path('updateuserprofile/<int:pk>/',views.updatestudentprofileView),
]