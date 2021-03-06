from django.contrib import admin
from .models import (
    Chat,
    Message,
    AnonymousUser
)

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(AnonymousUser)
