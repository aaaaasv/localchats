from django.contrib import admin
from accounts.models import AnonymousUser, User

admin.site.register(AnonymousUser)
admin.site.register(User)
