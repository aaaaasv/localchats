from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point

from geochats.models import PointCenter


def get_or_create_chat(radius, user_location):
    chats = get_chat(radius, user_location)
    if len(chats) == 0:
        chat = create_chat(user_location)
    else:
        chat = chats[0]

    return chat


def get_chat(radius, user_location):
    chats = PointCenter.objects.all().filter(
        location__distance_lt=(
            user_location,
            Distance(m=radius)
        )
    )
    return chats


def create_chat(location):
    lng = list(str(location.coords[0]))
    lat = list(str(location.coords[1]))
    lng[6], lat[6] = "5", "5"
    chat_lng = float("".join(lng))
    chat_lat = float("".join(lat))

    new_chat = PointCenter.objects.create(
        location=Point(chat_lng, chat_lat)
    )
    return new_chat
