from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point

from django.conf import settings

from geochats.models import Chat

radius = settings.CHAT_IN_RADIUS

# key_sector_coords = (50.43216, 30.52504) # seed
key_sector_coords = (50.805641, 30.130366)  # seed


def get_or_create_chat(user_location):
    chats = get_chat(user_location)
    if len(chats) == 0:
        create_chat(user_location)
        chat = get_chat(user_location)[0]
    else:
        chat = chats[0]

    return chat


def get_chat(user_location):
    chats = Chat.objects.all().filter(
        location__distance_lt=(
            user_location,
            Distance(m=radius)
        )
    )
    # try:
    #     raise TypeError(
    #         'user_location: ', user_location.coords,
    #         'created_chat: ', Chat.objects.all().first().location.coords,
    #         get_distance(Chat.objects.all().first().location, user_location),
    #         chats,
    #     )
    # except AttributeError:
    #     create_chat(user_location)
    return chats


def create_chat(location):
    t = ChatRetrievingTriangle(key_sector=(50.43216, 30.52504), person_location=(location[1], location[0]))
    Chat.objects.create(location=t.get_new_center())


from math import sqrt


def get_distance(person_location, new_center):
    geod = Geod(ellps='WGS84')
    _, _, distance = geod.inv(person_location[1], person_location[0],
                              new_center[1], new_center[0])
    return distance


from pyproj import Geod

geoid = Geod(ellps='WGS84')


class ChatRetrievingTriangle:
    def __init__(self, key_sector, person_location):
        self.key_sector_center = Point(*key_sector)
        self.person_location = Point(*person_location)
        print("USER LOCATION:", self.person_location)
        self.intersection_point = self.get_intersection_point()

    def get_intersection_point(self):
        return Point(self.person_location.coords[0], self.key_sector_center.coords[1])

    def get_difference(self, point1, point2):
        geod = Geod(ellps='WGS84')
        _, _, distance = geod.inv(point1[1], point1[0],
                                  point2[1], point2[0])
        print("DISTANCE: ", distance)
        integer_squares = distance // settings.CHAT_SQUARE_SIDE
        print("INTEGER SQUARES: ", integer_squares)
        return integer_squares * settings.CHAT_SQUARE_SIDE

    def get_lat(self):
        """
        :return: new latitude.
        """
        difference_m = self.get_difference(self.key_sector_center, self.intersection_point)
        if self.person_location[0] > self.key_sector_center[0]:
            az = 0
        elif self.person_location[0] < self.key_sector_center[0]:
            az = 180
        else:
            return self.intersection_point[0]

        self.intersection_point_new = self.move_point(self.key_sector_center, az, difference_m)
        return self.intersection_point_new[0]

    def get_lng(self):
        """
        :return: new longitude.
        """
        difference_m = self.get_difference(self.intersection_point, self.person_location)

        if self.person_location[1] > self.key_sector_center[1]:
            az = 90
        elif self.person_location[1] < self.key_sector_center[1]:
            az = 270
        else:
            return self.person_location[1]

        self.person_location_new = self.move_point(self.intersection_point, az, difference_m)

        return self.person_location_new.coords[1]

    def get_new_center(self):

        new_center = Point(self.get_lng(), self.get_lat())

        return new_center

    @staticmethod
    def _add_distance(lat, lng, az, dist):
        lng_new, lat_new, return_az = geoid.fwd(lng, lat, az, dist)
        return lat_new, lng_new

    def move_point(self, point, az, dist):
        lat, lng = self._add_distance(point.x, point.y, az, dist)
        return Point(lat, lng)


def update_room_id(request):
    lat = float(request.session['lat'])
    lng = float(request.session['lng'])
    point = Point(lng, lat)
    chat = get_or_create_chat(point)
    request.session['room_id'] = chat.id
