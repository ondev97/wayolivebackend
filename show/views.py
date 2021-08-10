import hashlib
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from aifc import Error
from authentication.serializer import UserProfileSerializer
from .serializer import *
from .filter import *
from rest_framework.pagination import PageNumberPagination
from .models import *


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createevent(request,pk):
    e_mode = EventMode.objects.get(id=pk)
    band = BandProfile.objects.get(user=request.user)
    event = Event(event_mode=e_mode, band=band)
    serializer = EventSerializer(event, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listevent(request,pk):
    event_mode = EventMode.objects.get(id=pk)
    events = Event.objects.filter(event_mode__id=event_mode.id)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listeventinband(request,pk):
    band = BandProfile.objects.get(id=pk)
    events = Event.objects.filter(band=band)
    filtered_events = EventFilter(request.GET, queryset=events)
    serializer = EventViewSerializer(filtered_events.qs, many=True)
    i = 0
    for d in serializer.data:
        serializer.data[i]['band']['user'].pop('password')
        e = Enrollment.objects.filter(event__id=d['id'], user__user=request.user)
        if e:
            serializer.data[i]['is_enrolled'] = True
        i = i+1

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def viewevent(request,pk):
    event = Event.objects.get(id=pk)
    serializer = EventViewSerializer(event)
    data = serializer.data
    e = Enrollment.objects.filter(event__id=serializer.data['id'],user__user=request.user)
    if e:
        data['is_enrolled'] = True
    data['band']['user'].pop('password')
    return Response(data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateevent(request,pk, id):
    event = Event.objects.get(id=pk)
    if id!=0:
        event_mode = EventMode.objects.get(id=id)
        event.event_mode = event_mode
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
def createeventmode(request):
    band = BandProfile.objects.get(user=request.user)
    concert = EventMode(band=band)
    serializer = EventModeSerializer(concert, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listeventmode(request):
    band = BandProfile.objects.get(user=request.user)
    eventmodes = EventMode.objects.filter(band=band)
    serializer = EventModeListSerializer(eventmodes, many=True)
    for i in range(len(serializer.data)):
        serializer.data[i]['band']['user'].pop('password')
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vieweventmode(request, pk):
    concert = EventMode.objects.get(id=pk)
    serializer = EventModeListSerializer(concert)
    serializer.data['band']['user'].pop('password')
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateeventmode(request, pk):
    concert = EventMode.objects.get(id=pk)
    serializer = EventModeSerializer(instance=concert, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteeventmode(request, pk):
    concert = EventMode.objects.get(id=pk)
    concert.delete()
    return Response({"message": "Event mode successfully deleted"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ticketgenerator(request, count, pk):
    event = Event.objects.filter(id=pk).first()
    try:
        Ticket.objects.bulk_create(
            [
                Ticket(event=event, ticket_number="")
                for __ in range(count)
            ]
        )
        TicketList = Ticket.objects.filter(ticket_number="")
        for t in list(TicketList):
            serializer = TicketSerializer(instance=t, data=request.data)
            if serializer.is_valid():
                ticket = str(t.id) + ":" + str(t.event.id)
                ticket_number = hashlib.shake_256(ticket.encode()).hexdigest(5)
                serializer.save(ticket_number=ticket_number)
        return Response({"message":"successfully created"})
    except Error:
        return  Response({"message":"Unable to create the bulk of Tickets"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def availabletickets(request, pk):
    event = Event.objects.get(id=pk)
    ticketList = Ticket.objects.filter(isValid=True, isIssued=False, event=event )
    serializer = TicketSerializer(ticketList, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def issuedtickets(request, pk):
    event = Event.objects.get(id=pk)
    ticketList = Ticket.objects.filter(isValid=True, isIssued=True, event=event)
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
def addtoevent(request, eid):
    event = Event.objects.get(id=eid)
    user = UserProfile.objects.get(user=request.user)
    ticketList = Ticket.objects.filter(event=event)
    for t in ticketList:
        if str(request.data['ticket_number']) == str(t.ticket_number):
            enroll = Enrollment(event=event,user=user, ticket_number=request.data['ticket_number'])
            condition = t.isValid==True and t.isIssued == True
            if request.method == "POST":
                if condition:
                    e = Enrollment.objects.filter(event=event, user=user).first()
                    if not e:
                        serializer = EnrollSerializer(enroll, data=request.data)
                        if serializer.is_valid():
                            serializer.save()
                            ticketserializer = TicketSerializer(instance=t, data=request.data)
                            if ticketserializer.is_valid():
                                ticketserializer.save(isValid=False)
                            return Response(serializer.data)
                        return Response(serializer.errors,status=403)
                    return Response({"message":"You have already in this event..."},status=403)
                return Response({"message":"Ticket is not valid"},status=403)

    return Response({"message":"ticket is not found"},status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addtoeventbyband(request, eid):
    event = Event.objects.get(id=eid)
    res = []
    for username in request.data['users']:
        user = UserProfile.objects.filter(user__username=username).first()
        if user:
            e = Enrollment.objects.filter(event=event, user=user).first()
            if not e:
                enroll = Enrollment(event=event, user=user, ticket_number="added by Band")
                serializer = EnrollSerializer(enroll, data= request.data)
                if serializer.is_valid():
                    serializer.save()
                    res.append({
                        "username" : user.user.username,
                        "email" : user.user.email,
                        "status" : "added to the event successfully",
                        "success": True
                    })
                else:
                    res.append({
                        "username": user.user.username,
                        "email": user.user.email,
                        "status": "something is wrong",
                        "success": False
                    })
            else:
                res.append({
                    "username": user.user.username,
                    "email": user.user.email,
                    "status": "already in this event",
                    "success": False
                })
        else:
            res.append({
                "username": username,
                "status": "user not found",
                "success": False
            })

    return Response(res, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def freeentry(request,eid):
    event = Event.objects.get(id=eid)
    user = UserProfile.objects.get(user=request.user)
    enrollment = Enrollment.objects.filter(user=user, event=event).first()
    if not enrollment:
        enroll = Enrollment(event=event, user=user, ticket_number="Free")
        enroll_serializer = EnrollSerializer(enroll, data=request.data)
        if enroll_serializer.is_valid():
            enroll_serializer.save()
            return Response(enroll_serializer.data)
        return Response(enroll_serializer.errors)
    else:
        return Response({'message': 'You have already enrolled'}, status=403)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def removefromevent(request, uid, eid):
    user = UserProfile.objects.get(id=uid)
    event = Event.objects.get(id=eid)
    enrollment = Enrollment.objects.filter(event=event, user=user).first()
    if enrollment:
        enrollment.delete()
        return Response({'message' : 'Removed successfully'}, status=200)
    else:
        return Response({'message': 'No entry found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def purchasedevent(request,eid):
    event = Event.objects.get(id=eid)
    user = UserProfile.objects.get(user=request.user)
    enrollment = Enrollment.objects.filter(user=user, event=event).first()
    if not enrollment:
        enroll = Enrollment(event=event, user=user, ticket_number="Purchased", is_payment=True)
        enroll_serializer = EnrollSerializer(enroll, data=request.data)
        if enroll_serializer.is_valid():
            enroll_serializer.save()
            return Response(enroll_serializer.data)
        return Response(enroll_serializer.errors)
    else:
        return Response({'message': 'You have already enrolled'}, status=403)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkpayment(request, eid):
    event = Event.objects.get(id=eid)
    user = UserProfile.objects.get(user=request.user)
    enrollment = Enrollment.objects.filter(user=user, event=event).first()
    enrollments = Enrollment.objects.filter(event=event)
    u = UserProfileSerializer(user)
    if enrollment:
        return Response({'is_payable': False, 'enrolled': True}, status=200)

    if event.limit > len(enrollments):
        return Response({'is_payable': True, 'payment_id': user.id+'-'+event.id, 'user': u.data}, status=200)

    else:
        return Response({'is_payable': False, 'enrolled': False}, status=200)


@api_view(['POST'])
def notifyurl(request, uid, eid):
    event = Event.objects.get(id=eid)
    user = UserProfile.objects.get(user_id=uid)

    payment = Payment(user=user, event=event)
    payment_serializer = PaymentSerializer(payment, data=request.data)
    if payment_serializer.is_valid():
        payment_serializer.save()

    if str(request.data['status_code']) == '2':
        enrollment = Enrollment.objects.filter(user=user, event=event).first()
        if not enrollment:
            enroll = Enrollment.objects.create(event=event, user=user, ticket_number="Purchased", is_payment=True)
            return Response({'message': 'success'}, status=200)
        else:
            return Response({'message': 'already enrolled'}, status=403)
    else:
        return Response({'message': 'payment error'}, status=403)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eventsinband(request):
    band = BandProfile.objects.get(user=request.user)
    events = Event.objects.filter(band=band)
    serializer = EventViewSerializer(events,many=True)
    for i in range(len(serializer.data)):
        serializer.data[i]['band']['user'].pop('password')
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audienceinthevent(request,pk):
    event = Event.objects.get(id=pk)
    events_enrolled = Enrollment.objects.filter(event=event).order_by('-id')
    user_ids = []
    for c in events_enrolled:
        if c.user.id not in user_ids:
            user_ids.append(c.user.id)
    users = UserProfile.objects.filter(id__in=user_ids)
    paginator = PageNumberPagination()
    paginator.page_size = 100
    result_page = paginator.paginate_queryset(users,request)
    serializer = UserProfileSerializer(result_page, many=True)
    for i in range(len(serializer.data)):
        serializer.data[i]['user'].pop('password')
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def myevents(request):
    user = UserProfile.objects.get(user_id=request.user.id)
    events_enrolled = Enrollment.objects.filter(user=user).order_by('-id')
    serializer = MyEventsSerializer(events_enrolled,many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def eventmodesforuser(request,pk):
    band = BandProfile.objects.get(id=pk)
    event_modes = EventMode.objects.filter(band=band)
    serializer = EventModeSerializer(event_modes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def audiencedatacollect(request):
    serializer = AudienceDataSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=200)
    else:
        return Response({
            "err":"Something Went Wrong"
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latestevent(request):
    event = Event.objects.filter().order_by('-event_date').first()
    if event:
        serializer = EventSerializer(event)
        return Response(serializer.data)
    else:
        return Response('no data found', status=404)

