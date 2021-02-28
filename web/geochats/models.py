from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


class Zipcode(models.Model):
    code = models.CharField(max_length=5)
    poly = models.PolygonField()


class Elevation(models.Model):
    name = models.CharField(max_length=100)
    rast = models.RasterField()


class PointCenter(models.Model):
    location = models.PointField(geography=True, default=Point(0.0, 0.0))


class Message(models.Model):
    text = models.CharField(max_length=500)
    chat = models.ForeignKey(PointCenter, on_delete=models.CASCADE)