from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point

from django.conf import settings

from geochats.models import PointCenter


def get_or_create_chat(radius, user_location):
    chats = get_chat(radius, user_location)
    if len(chats) == 0:
        create_chat(radius, user_location)
        chat = get_chat(radius, user_location)[0]
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


def create_chat(radius, location):
    lng = list(str(location.coords[0]))
    lat = list(str(location.coords[1]))
    lng[6], lat[6] = "5", "5"
    chat_lng = float("".join(lng))
    chat_lat = float("".join(lat))

    new_chat = PointCenter.objects.create(
        location=Point(chat_lng, chat_lat)
    )


from math import sin, cos, sqrt, atan2, radians
from pyproj import Geod

geoid = Geod(ellps='WGS84')


class ChatRetrievingTriangle:
    def __init__(self, key_sector, person_location):
        self.key_sector_center = Point(*key_sector)
        self.person_location = Point(*person_location)
        self.intersection_point = self.get_intersection_point()

    def get_intersection_point(self):
        return Point(self.person_location.coords[0], self.key_sector_center.coords[1])

    def get_difference(self, point1, point2):

        # approximate radius of earth in km
        # R = 6373.0
        #
        # lat1 = radians(point1[0])
        # lon1 = radians(point1[1])
        # lat2 = radians(point2[0])
        # lon2 = radians(point2[1])
        #
        # dlon = lon2 - lon1
        # dlat = lat2 - lat1
        #
        # a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        # c = 2 * atan2(sqrt(a), sqrt(1 - a))
        #
        # distance = R * c  # km
        # distance *= 100
        geod = Geod(ellps='WGS84')
        _, _, distance = geod.inv(point1[1], point1[0],
                                  point2[1], point2[0])
        integer_squares = distance // settings.CHAT_SQUARE_SIDE
        return integer_squares * settings.CHAT_SQUARE_SIDE

    def get_lat(self):
        """
        :return: new latitude.
        """
        difference_m = self.get_difference(self.key_sector_center, self.intersection_point)
        if self.person_location[0] > self.key_sector_center[0]:
            # az = 90  # up (north)
            az = 0
        elif self.person_location[0] < self.key_sector_center[0]:
            az = 180
            # az = 270  # down (south)
        else:
            print("DIFFERENCE IS ZERO")
            return self.intersection_point[0]
        self.intersection_point_new = self.move_point_north(self.key_sector_center, az, difference_m)
        return self.intersection_point_new[0]

    def get_lng(self):
        """
        :return: new longitude.
        """
        difference_m = self.get_difference(self.intersection_point, self.person_location)

        if self.person_location[1] > self.key_sector_center[1]:
            az = 90
            # az = 0  # right (east)
        elif self.person_location[1] < self.key_sector_center[1]:

            # az = 180  # left (west)
            az = 270
        else:
            return self.person_location[1]
        self.person_location_new = self.move_point_north(self.intersection_point, az, difference_m)

        return self.person_location_new.coords[1]

    def get_new_center(self):

        new_center = Point(self.get_lat(), self.get_lng())

        return new_center

    @staticmethod
    def _add_distance(lat, lng, az, dist):
        lng_new, lat_new, return_az = geoid.fwd(lng, lat, az, dist)
        return lat_new, lng_new

    def move_point_north(self, point, az, dist):
        lat, lng = self._add_distance(point.x, point.y, az, dist)
        return Point(lat, lng)

# t = ChatRetrievingTriangle((50.43216, 30.52504), (50.27752, 29.82452))
# print(t.get_new_center())

# t.get_difference(t.key_sector_center, t.intersection_point)

# print(t.get_new_center())

# t = ChatRetrievingTriangle((50.43216, 30.52504), (50.27762, 29.82432))
# print(t.get_new_center())

# t.get_difference(t.key_sector_center, t.intersection_point)

# print(t.get_new_center())


# t = ChatRetrievingTriangle((50.43216, 30.52504), (50.2770469250185, 29.86197))
# t = ChatRetrievingTriangle((50.43216, 30.52504), (49.663826, 31.524205))

# print(t.get_new_center())


# moving intersection point
# class ChatRetrievingTriangle:
#     def __init__(self, key_sector, person_location):
#         self.key_sector_center = Point(*key_sector)
#         self.person_location = Point(*person_location)
#         self.intersection_point = self.get_intersection_point()
#
#         print("OLD INTERSECTION LATITUDE: ", self.intersection_point[0])
#
#     def get_intersection_point(self):
#         return Point(self.person_location.coords[0], self.key_sector_center.coords[1])
#
#     def get_difference(self, point1, point2):
#
#         # approximate radius of earth in km
#         R = 6373.0
#
#         lat1 = radians(point1[0])
#         lon1 = radians(point1[1])
#         lat2 = radians(point2[0])
#         lon2 = radians(point2[1])
#
#         dlon = lon2 - lon1
#         dlat = lat2 - lat1
#
#         a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
#         c = 2 * atan2(sqrt(a), sqrt(1 - a))
#
#         distance = R * c  # km
#         distance *= 100
#         geod = Geod(ellps='WGS84')
#         angle1, angle2, distance = geod.inv(point1[1], point1[0],
#                                             point2[1], point2[0])
#         # how many squares are in the distance between main section center and intersection point
#         count_squares = distance / settings.CHAT_SQUARE_SIDE
#         # how many full squares
#         integer_squares = round(count_squares)
#         print("INT SQUARES:", integer_squares)
#         difference = abs(count_squares - integer_squares)
#         print("DIFFERENCE IN SQUARES: ", difference)
#         difference_m = difference * settings.CHAT_SQUARE_SIDE
#         print("DIFFERENCE", difference_m, "m")
#         return round(difference_m, 3)
#
#         # return -(integer_squares * settings.CHAT_SQUARE_SIDE)
#
#     def get_lat(self):
#         """
#         :return: new latitude.
#         """
#         # geod = Geod(ellps='WGS84')
#         # angle1, angle2, distance1 = geod.inv(self.key_sector_center[1], self.key_sector_center[0],
#         #                                     self.intersection_point[1], self.intersection_point[0])
#
#         difference_m = self.get_difference(self.key_sector_center, self.intersection_point)
#
#         print("Latitude moved by", difference_m, "m")
#         print("INTERSECTION POINT: ", self.intersection_point)
#         if difference_m > 0:
#             # az = 90  # up (north)
#             az = 0
#         elif difference_m < 0:
#             az = 180
#             # az = 270  # down (south)
#         print("AZIMUTH: ", az)
#         # self.intersection_point_new = self.move_point_north(self.intersection_point, az, difference_m / 1000)
#         print("OLD LATITUDE: ", self.intersection_point[0])
#         self.intersection_point_new = self.move_point_north(self.intersection_point, az, abs(difference_m))# / 1000)
#         print("NEW LATITUDE: ", self.intersection_point_new[0])
#         return self.intersection_point_new[0]
#
#     def get_lng(self):
#         """
#         :return: new longitude.
#         """
#         difference_m = self.get_difference(self.intersection_point, self.person_location)
#
#         print("Person location:", self.person_location)
#
#         if difference_m > 0:
#             print("Long to right")
#             # az = 90
#             az = 0  # right (east)
#         elif difference_m < 0:
#             print("Long to left")
#             difference_m = abs(difference_m)
#             az = 180  # left (west)
#             # az = 270
#         print("Longitude moved by", difference_m, "m")
#
#         self.person_location_new = self.move_point_north(self.person_location, az, difference_m / 1000)
#
#         return self.person_location_new.coords[1]
#
#     def get_new_center(self):
#         return Point(self.get_lat(), self.get_lng())
#
#     @staticmethod
#     def _add_distance(lat, lng, az, dist):
#         lng_new, lat_new, return_az = geoid.fwd(lng, lat, az, dist)
#         return lat_new, lng_new
#
#     def move_point_north(self, point, az, dist):
#         lat, lng = self._add_distance(point.x, point.y, az, dist)
#         return Point(lat, lng)
#
#
# # t = ChatRetrievingTriangle((50.43216, 30.52504), (49.90695, 31.74316))
#
# t = ChatRetrievingTriangle((50.43216, 30.52504), (50.27765, 29.82452))
# # print(t.get_new_center())
#
# # t.get_difference(t.key_sector_center, t.intersection_point)
#
# print(t.get_lat())
#
# t = ChatRetrievingTriangle((50.43216, 30.52504), (50.27762, 29.82432))
# # print(t.get_new_center())
#
# # t.get_difference(t.key_sector_center, t.intersection_point)
#
# print(t.get_lat())
