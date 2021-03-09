from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.gis.geos import Point

from geochats.models import Message, Chat, AnonymousUser
from geochats.services import (
    update_room_id
)


def index(request):
    return render(request, 'geochats/index.html', {})


def room(request):
    # raise TypeError(request.session['user_id'])
    # user = AnonymousUser.objects.create()
    # print(AnonymousUser.objects.get(id=request.session['user_id']).username)
    return render(request, 'geochats/room.html',
                  {
                      'messages': None,
                      'user': None
                  })


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def ajax_save_user(request):
    user_id = request.POST.get('user_id', None)

    if user_id:
        request.session['user_id'] = user_id
        request.session['user_persistence'] = True
    return JsonResponse({'success': "Ok"})


def ajax_get_location(request):
    request.session['lat'] = request.GET['lat']
    request.session['lng'] = request.GET['lng']
    # print(request.session[])
    request.session['timezone'] = request.GET['time_offset']
    old_chat = request.session.get('room_id')

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
    points = []
    for i in Chat.objects.all():
        points.append([i.location[0], i.location[1]])
    context = {
        # 'points': [[30.1345542, 50.8018212], [30.1303865, 50.8059638]]
        'points': points
    }

    return render(request, 'geochats/map-test.html', context)
