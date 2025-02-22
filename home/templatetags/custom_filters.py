from django import template
from datetime import timedelta
from django.utils.timezone import now

register = template.Library()

@register.filter
def custom_timesince(value):
    if not value:
        return ""

    time_difference = now() - value

    if time_difference < timedelta(hours=1):
        minutes = time_difference.seconds // 60
        return f"{minutes} min ago"
    elif time_difference < timedelta(days=1):
        hours = time_difference.seconds // 3600
        return f"{hours} hr ago"
    elif time_difference < timedelta(days=30):
        days = time_difference.days
        return f"{days} days ago"
    elif time_difference < timedelta(days=365):
        months = time_difference.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = time_difference.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
