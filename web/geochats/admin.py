from django.contrib import admin
from .models import (
    Chat,
    AuthMessage,
    AnonMessage
)

admin.site.register(Chat)
admin.site.register(AnonMessage)
admin.site.register(AuthMessage)
