from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib.gis.geos import Point

from geochats.models import Message, PointCenter
from geochats.services import get_or_create_chat


def index(request):
    return render(request, 'geochats/index.html', {})


def room(request):
    radius = settings.CHAT_IN_RADIUS
    lat = float(request.session['lat'])
    lng = float(request.session['lng'])
    point = Point(lng, lat)
    chat = get_or_create_chat(radius, point)
    request.session['room_id'] = chat.id
    messages = PointCenter.objects.get(id=chat.id).message_set.all()
    return render(request, 'geochats/room.html',
                  {
                      'messages': messages
                  })


def ajax_get_location(request):
    request.session['lat'] = request.GET['lat']
    request.session['lng'] = request.GET['lng']
    return JsonResponse({'room_id': 'None'})


def map_test(request):
    context = {
        'points': None
    }

    return render(request, 'geochats/map-test.html', context)
