from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.gis.geos import Point

from geochats.models import Message, PointCenter
from geochats.services import (
    update_room_id
)


def index(request):
    return render(request, 'geochats/index.html', {})


def room(request):
    update_room_id(request)
    messages = PointCenter.objects.get(id=request.session['room_id']).message_set.all()
    return render(request, 'geochats/room.html',
                  {
                      'messages': messages
                  })


def ajax_get_location(request):
    request.session['lat'] = request.GET['lat']
    request.session['lng'] = request.GET['lng']
    old_chat = request.session['room_id']
    update_room_id(request)
    new_chat = request.session['room_id']
    if old_chat != new_chat:
        context = {
            'updated': True
        }
    else:
        context = {
            'updated': False
        }
    return JsonResponse(context)


def map_test(request):
    context = {
        'points': [[30.1345542, 50.8018212 ], [30.1303865, 50.8059638]]
    }

    return render(request, 'geochats/map-test.html', context)
