from django import template
# from django.utils import timezone
import pytz
from datetime import timezone, datetime

register = template.Library()


@register.filter
def convert_timezone(date, user_timezone):
    user_timezone = pytz.timezone(user_timezone)
    date.replace(tzinfo=timezone.utc)
    return date.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone(str(user_timezone)))

