from django.urls import path,include
from . import views

urlpatterns = [

    # concert urls

    path('createconcert/',views.createconcert),
    path('listconcert/',views.listconcert),
    path('viewconcert/<int:pk>/',views.viewconcert),
    path('updateconcert/<int:pk>/',views.updateconcert),
    path('deleteconcert/<int:pk>/',views.deleteconcert),


    # event urls

    path('createevent/<int:pk>/',views.createevent),
    path('listevents/<int:pk>/',views.listevent),
    path('viewevent/<int:pk>/',views.viewevent),
    path('updateevent/<int:pk>/',views.updateevent),
    path('deleteevent/<int:pk>/',views.deletevent),

    # ticket urls

    path('createticket/<int:pk>/<int:count>/',views.ticketgenerator),
    path('listticket/<int:pk>/',views.availabletickets),
    path('issuedtickets/<int:pk>/',views.issuedtickets),
    path('issueticket/',views.issueticket),

    # adding to the concert

    path('addtoconcert/<int:pk>/',views.addtoconcert),
    path('addtoconcertbyband/<int:pk>/',views.addtoconcertbyband),
    path('freeconcert/<int:cid>/',views.freeentry),
    path('remove/<int:cid>/<int:uid>/',views.removefromconcert),




]