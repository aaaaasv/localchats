from math import sqrt

from django.test import SimpleTestCase
from django.conf import settings
from pyproj import Geod

from geochats.services import ChatRetrievingTriangle


class TestChatRetrieving(SimpleTestCase):

    def test_distance_between_user_position_and_create_chat_center(self):

        key_sector = (50.43216, 30.52504)

        points = [[30.52504, 50.43216], ]

        from_lat = 30.59
        to_lat = 30.6
        from_lng = 50.49
        to_lng = 50.5

        import random
        counter = 0
        test_count = 500
        for i in range(test_count):
            coord1 = random.uniform(from_lng, to_lng)
            coord2 = random.uniform(from_lat, to_lat)
            t = ChatRetrievingTriangle(key_sector, (coord1, coord2))
            result_test = self.get_distance(t.person_location, t.get_new_center())
            if result_test == 1:
                counter += 1
            points.append([t.get_lng(), t.get_lat()])

        self.assertEqual(counter, 0)

    def get_distance(self, person_location, new_center):
        geod = Geod(ellps='WGS84')
        _, _, distance = geod.inv(person_location[1], person_location[0],
                                  new_center[1], new_center[0])
        if distance > settings.CHAT_SQUARE_SIDE*sqrt(2):
            return 1
