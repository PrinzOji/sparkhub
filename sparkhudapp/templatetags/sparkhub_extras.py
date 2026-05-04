from django import template
from django.contrib.auth.models import Group
from sparkhudapp.models import Like

register = template.Library()

@register.filter
def has_group(user, group_name):
    """Check if user belongs to a specific group"""
    try:
        group = Group.objects.get(name=group_name)
        return group in user.groups.all()
    except Group.DoesNotExist:
        return False

@register.filter
def user_can_register(event, user):
    """Check if user can register for event (has enough points and not already registered)"""
    if not user.is_authenticated:
        return False
    try:
        profile = user.userprofile
        already_registered = event.eventregistration_set.filter(user=user).exists()
        return profile.points >= event.required_points and not already_registered
    except:
        return False

@register.filter
def user_attended(event, user):
    """Check if user attended a specific event"""
    if not user.is_authenticated:
        return False
    try:
        registration = event.eventregistration_set.get(user=user)
        return registration.attended
    except:
        return False

@register.filter
def floatdiv(value, arg):
    """Divide two values and return float"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply two values."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def has_liked_post(user, post_id):
    """Check if user has liked a specific post"""
    if not user.is_authenticated:
        return False
    try:
        return Like.objects.filter(user=user, post_id=post_id).exists()
    except:
        return False

@register.filter
def count_attended(events):
    """Count attended events in a queryset"""
    try:
        return events.filter(attended=True).count()
    except:
        return 0
