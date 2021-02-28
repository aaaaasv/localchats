from django.contrib import admin
from .models import (
    Elevation,
    Zipcode,
    PointCenter,
    Message
)

admin.site.register(Elevation)
admin.site.register(Zipcode)
admin.site.register(PointCenter)
admin.site.register(Message)
