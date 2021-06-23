from django.urls import path,include
from . import views

urlpatterns = [

    # event mode urls

    path('createeventmode/', views.createeventmode),
    path('listeventmode/', views.listeventmode),
    path('vieweventmode/<int:pk>/', views.vieweventmode),
    path('updateeventmode/<int:pk>/', views.updateeventmode),
    path('deleteeventmode/<int:pk>/', views.deleteeventmode),
    path('myeventmodes/<int:pk>/', views.eventmodesforuser),


    # event urls

    path('createevent/<int:pk>/',views.createevent),
    path('listevents/<int:pk>/',views.listevent),
    path('listeventsinband/<int:pk>/',views.listeventinband),
    path('viewevent/<int:pk>/',views.viewevent),
    path('updateevent/<int:pk>/<int:id>/',views.updateevent),
    path('deleteevent/<int:pk>/',views.deletevent),

    # ticket urls

    path('createticket/<int:pk>/<int:count>/',views.ticketgenerator),
    path('listticket/<int:pk>/',views.availabletickets),
    path('issuedtickets/<int:pk>/',views.issuedtickets),
    path('issueticket/',views.issueticket),

    # adding to the concert

    path('addtoevent/<int:eid>/', views.addtoevent),
    path('addtoeventbyband/<int:eid>/', views.addtoeventbyband),
    path('freeevent/<int:eid>/',views.freeentry),
    path('remove/<int:eid>/<int:uid>/', views.removefromevent),

    # events in band

    path('eventsinband/',views.eventsinband),

    # audience in the event

    path('audienceintheevent/<int:pk>/',views.audienceinthevent),

    # my events

    path('myevents/',views.myevents),




]