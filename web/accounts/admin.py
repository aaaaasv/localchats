from django.contrib import admin
from accounts.models import AnonymousUser, User, Username
from django.contrib.auth.admin import UserAdmin

admin.site.register(AnonymousUser)
admin.site.register(User, UserAdmin)
admin.site.register(Username)
