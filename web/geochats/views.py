from django.http import JsonResponse
from django.shortcuts import render

from geochats.models import Message, PointCenter


def index(request):
    return render(request, 'geochats/index.html', {})


def room(request, room_name):

    # messages = PointCenter.objects.get(id=request.session['room_id']).message_set
    messages = PointCenter.objects.get(id=4).message_set.all()
    return render(request, 'geochats/room.html',
                  {
                      'room_name': room_name,
                      'messages': messages
                  })


def ajax_get_location(request):
    request.session['lat'] = request.GET['lat']
    request.session['lng'] = request.GET['lng']
    return JsonResponse({'Data': 'Ok'})
