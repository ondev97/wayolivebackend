import hashlib

from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from aifc import Error

from .serializer import *

from .models import *


# Band Views

# def createBand(request):
#     pass
#
# def listBand(request):
#     pass
#
# def viewBand(request,pk):
#     pass
#
#
# def updateBand(request,pk):
#     pass
#
# def deleteBand(request,pk):
#     pass
#

# show Views

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createevent(request,pk):
    concert = Concert.objects.get(id=pk)
    event = Event(concert=concert)
    serializer = EventSerializer(event, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listevent(request,pk):
    concert = Concert.objects.get(id=pk)
    events = Event.objects.filter(concert__id=concert.id)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewevent(request,pk):
    event = Event.objects.get(id=pk)
    serializer = EventViewSerializer(event)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateevent(request,pk):
    event = Event.objects.get(id=pk)
    serializer = EventSerializer(instance=event,data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletevent(request,pk):
    event = Event.objects.get(id=pk)
    event.delete()
    return Response({"message": "Concert Successfully Deleted"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createconcert(request):
    band = BandProfile.objects.get(user=request.user)
    concert = Concert(band=band)
    serializer = ConcertSerializer(concert, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listconcert(request):
    concerts = Concert.objects.all()
    serializer = ConcertListSerializer(concerts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewconcert(request,pk):
    concert = Concert.objects.get(id=pk)
    serializer = ConcertListSerializer(concert)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateconcert(request,pk):
    concert = Concert.objects.get(id=pk)
    serializer = ConcertSerializer(instance=concert,data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteconcert(request,pk):
    concert = Concert.objects.get(id=pk)
    concert.delete()
    return Response({"message": "Concert Successfully Deleted"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticketgenerator(request, count, pk):
    concert = Concert.objects.filter(id=pk).first()
    try:
        Ticket.objects.bulk_create(
            [
                Ticket(concert=concert, ticket_number="")
                for __ in range(count)
            ]
        )
        TicketList = Ticket.objects.filter(ticket_number="")
        for t in list(TicketList):
            serializer = TicketSerializer(instance=t, data=request.data)
            if serializer.is_valid():
                ticket = str(t.id) + ":" + str(t.concert.id)
                ticket_number = hashlib.shake_256(ticket.encode()).hexdigest(5)
                serializer.save(ticket_number=ticket_number)
        return Response({"message":"successfully created"})
    except Error:
        return  Response({"message":"Unable to create the bulk of Tickets"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def availabletickets(request, pk):
    concert = Concert.objects.get(id=pk)
    ticketList = Ticket.objects.filter(isValid=True, isIssued=False, concert=concert )
    serializer = TicketSerializer(ticketList, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def issuedtickets(request, pk):
    concert = Concert.objects.get(id=pk)
    ticketList = Ticket.objects.filter(isValid=True, isIssued=True, concert=concert)
    serializer = TicketSerializer(ticketList, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issueticket(request):
    for i in range(len(request.data['issued_tickets'])):
        ticket = Ticket.objects.get(id=request.data['issued_tickets'][i])
        serializer = TicketSerializer(instance=ticket,data=request.data)
        if serializer.is_valid():
            serializer.save(isIssued=True)
    return Response({"message":"successfully issued"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addtoconcert(request,pk):
    concert = Concert.objects.get(id=pk)
    user = UserProfile.objects.get(user=request.user)
    ticketList = Ticket.objects.filter(concert=concert)
    for t in ticketList:
        if str(request.data['ticket_number']) == str(t.ticket_number):
            enroll = Enrollment(concert=concert,user=user, ticket_number=request.data['ticket_number'])
            condition = t.isValid==True and t.isIssued == True
            if request.method == "POST":
                if condition:
                    e = Enrollment.objects.filter(concert=concert, user=user).first()
                    if not e:
                        serializer = EnrollSerializer(enroll, data=request.data)
                        if serializer.is_valid():
                            serializer.save()
                            ticketserializer = TicketSerializer(instance=t, data=request.data)
                            if ticketserializer.is_valid():
                                ticketserializer.save(isValid=False)
                            return Response(serializer.data)
                        return Response(serializer.errors,status=403)
                    return Response({"message":"You have already enrolled this course..."},status=403)
                return Response({"message":"Coupon is not valid"},status=403)

    return Response({"message":"coupon is not found"},status=404)
